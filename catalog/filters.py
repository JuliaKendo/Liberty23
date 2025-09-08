import re
import ast
import json
import django_filters
from django_filters import BooleanFilter, CharFilter, BaseInFilter
from django.db.models import Count, Q, Case, When, IntegerField
from django.db.models import Value as V
from functools import reduce
from itertools import permutations

from .models import Product
from prices.models import Price, PriceType


class FilterTree(object):

    def __init__(self, qs=None):
        self.tree = []
        self.qs = qs
    
    def __serialize_root(self, root, root_field, **kwargs):
        def get_ident():
            ident_field = root_field
            if kwargs.get('ident'):
                ident_field = kwargs['ident']

            if root[ident_field]:
                return '%s_%s' % (
                    root_field,
                    re.sub(r'[^a-zA-Zа-яА-Я0-9]', '', str(root[ident_field])).lower()
                )
            return root_field
        
        return root | {'name': root_field, 'ident': get_ident()}

    def __serialize_node(self, parent, node, node_fields, **kwargs):
        def get_ident(item):
            result = ''
            for node_field in node_fields:
                if not item[node_field]:
                    continue
                result += '%s_%s_%s' % (
                    node_field,
                    re.sub(r'[^a-zA-Zа-яА-Я0-9]', '', parent).lower(),
                    re.sub(r'[^a-zA-Zа-яА-Я0-9]', '', item[node_field]).lower()
                )
            return result
        
        return [element for element in [item | {'name': '_'.join(node_fields), 'ident': get_ident(item)} for item in node] if element['ident']]

    def to_json(self):
        result = []
        for item in self.tree:
            result.append({key: value for key, value in item.items() if key != 'nodes'})

            if item.get('nodes'):
                result.extend([
                    {
                        key: value for key, value in node.items()
                    } for node in item['nodes']
                ])
        return result

    def count(self, root_field, *node_fields, **kwargs):        
        if self.qs:
            root_order = kwargs.get('root_order', [])
            node_order = kwargs.get('node_order', [])
            ident_field = kwargs.get('ident', '')
            if ident_field:
                qs = self.qs.values(root_field, ident_field).annotate(count=Count('id'))
            else:
                qs = self.qs.values(root_field).annotate(count=Count('id'))
            if root_order:
                qs = qs.order_by(*root_order)
            for root in qs:
                if not root[root_field]:
                    continue
                if node_fields:
                    node_qs = self.qs.filter(Q((root_field, root[root_field]))).values(*node_fields).annotate(count=Count('id'))
                    if node_order:
                        node_qs = node_qs.order_by(*node_order)   
                    if node_qs:
                        root['nodes'] = self.__serialize_node(root[root_field], node_qs, node_fields) 
                self.tree.append(self.__serialize_root(root, root_field, ident=ident_field))


class SearchFilter(object):
    
    def __init__(self, queryset, search_fields='', search_str=''):
        self.qs = queryset
        self.fields = search_fields
        self.search = search_str

    def _convert_values(self):
        result = []
        values = ast.literal_eval(self.search)
        search_params = [value for item in values for value in item.split()]
        for index in range(1, len(search_params)+1):
            items = []
            for search_param in permutations(search_params, (index)):
                items.append(' '.join(search_param))
            result = [*result, (index, items)]
        return result

    def apply_filter(self):
        querysets = []
        values = self._convert_values()
        for index, field in enumerate(self.fields):
            for relevance, items in values:
                queries = [Q((f'{field}', rf'\b{re.escape(item)}\b')) for item in items]
                qs = self.qs.annotate(source=V(f'{index}'))\
                    .filter(reduce(lambda field, val: field | val, queries))
                querysets.extend([{'obj': item, 'source': item.source, 'relevance': relevance} for item in qs])

        return querysets
    
    def get_filtered_qs(self, querysets):
        grp_keys = ('obj', 'source')
        sum_keys = ['relevance']
        result = [
            {
                **{grp_key: key[i] for i, grp_key in enumerate(grp_keys)},
                **{skey: sum(sub[skey] for sub in querysets if all(sub[k] == key[i] for i, k in enumerate(grp_keys)))}
            }
            for key in set(tuple(sub[k] for k in grp_keys) for sub in querysets)
            for skey in sum_keys
        ]
        result.sort(key=lambda i: (i['source'], -i['relevance']))

        result_qs = Product.objects.filter(pk__in=[item['obj'].id for item in result])
        return result_qs.annotate(
            custom_order=Case(
                *[When(pk=item['obj'].id, then=pos) for pos, item in enumerate(result)],
                default=len(result),
                output_field=IntegerField(),
            )
        ).order_by('custom_order')


class ProductFilter(django_filters.FilterSet):

    category = CharFilter(method='category_filter')
    price = django_filters.NumericRangeFilter(
        field_name='price',
        lookup_expr='range',
        method='price_filter'
    )
    search_values   = CharFilter(method='search_filter')

    class Meta:
        model = Product
        fields = ['category',]
    
    def category_filter(self, queryset, name, value):
        ids = ast.literal_eval(value)
        if ids:
            return queryset.filter(category_id__in=ids)
        return queryset

    def price_filter(self, queryset, name, value):
        filters = {}
        if value.start:
            filters[f'{name}__gte'] = value.start
        if value.stop:
            filters[f'{name}__lte'] = value.stop    
        return queryset.filter(
            pk__in=Price.objects.filter(
                type=PriceType.objects.get(name='Базовая'),
                **filters
            ).values_list('product_id', flat=True)
        )

    def search_filter(self, queryset, name, value):
        fields = ['articul__iregex', 'name__iregex', 'description__iregex',]
        search_obj = SearchFilter(queryset, fields, value)
        if search_obj._convert_values():
            return search_obj.get_filtered_qs(search_obj.apply_filter())
        return queryset
