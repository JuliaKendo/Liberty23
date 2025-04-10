import re
import base64
import imghdr
import mimetypes
import six

from django.conf import settings
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.core.files.base import ContentFile
from django.views.generic import ListView, DetailView, TemplateView
from contextlib import suppress
from more_itertools import first
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import (
    ModelSerializer, ListSerializer, ImageField
)
from rest_framework_recursive.fields import RecursiveField

from .filters import FilterTree, ProductFilter, SearchFilter

from .models import Category, Product, ProductImage
from prices.models import Price
from cart.cart import Cart


class FiltersView(TemplateView):
    template_name = 'components/products/filters.html'

    def get_filter(self, qs=None, func='', field='', *groups, **kwargs):
        if qs: 
            filter_tree = FilterTree(qs)
            method = getattr(filter_tree, func)
            method(field, *groups, **kwargs)
            return filter_tree
        return FilterTree()
    
    def get_filters(self, qs):
        filters = dict()
        filters['category'] = self.get_filter(qs, 'count', 'category__name', ident='category__id')
        # filters['price-range'] = self.get_filter()
        return filters

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filters'] = self.get_filters(Product.objects.all())
        return context


class ProductsView(FiltersView, ListView):
    model = Product
    template_name = 'products.html'
    context_object_name = 'products'
    allow_empty = True; paginate_by = 30; filters = {}
    default_sort = {'name': 'sort_ascending'}; sort_by = {}

    def update_value(self, key, default_value):
        self.request.session[key] = default_value
        current_value = {k: v for k, v in dict(self.request.POST).items() if k in [key,]}
        if current_value:
            self.filters = self.filters | current_value
            self.request.session[key] = current_value[key]


    def get(self, request, *args, **kwargs):
        self.filters = {
            k: v for k, v in dict(self.request.GET).items() if k != 'page'
        }

        search_values = self.request.session.get('search_values')
        if search_values:
            self.filters = self.filters | {'search_values': search_values}

        with suppress(IndexError):
            self.sort_by['name'] = self.request.session.get(
                'sort_by_product_name',
                [self.default_sort['name']]
            )[0]
            return super().get(request, *args, **kwargs)
        self.sort_by = self.default_sort
        return super().get(request, *args, **kwargs)


    def post(self, request, *args, **kwargs):
        self.update_value('search_values', [])
        self.update_value('sort_by_product_name', [self.default_sort['name']])
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        products = Product.objects.all()
        if self.filters:
            filtred_products = ProductFilter(self.filters, queryset=products)
            products = filtred_products.qs
        
        if 'name' in self.sort_by.keys():
            products = products.order_by('name')
            if self.sort_by['name'] == 'sort_descending':
                products = products.order_by('-name') 
   
        return products

    def get_context_data(self, *, object_list=None, **kwargs):
        self.object_list = self.get_queryset()
        context = super().get_context_data(**kwargs)

        paginator = Paginator(context['products'], self.paginate_by)
        page = self.request.GET.get('page')
        
        try:
            product_page = paginator.page(page)
        except PageNotAnInteger:
            product_page = paginator.page(1)
        except EmptyPage:
            product_page = paginator.page(paginator.num_pages)

        context['search_values'] = [
            item for elem in [value for key, value in self.filters.items() if key == 'search_values'] for item in elem
        ]
        context['sort_by']   = self.sort_by
        context['products']  = product_page
        context['prices']    = Price.objects.available_prices(product_page)
        context['MEDIA_URL'] = settings.MEDIA_URL

        return context


class ProductCardView(DetailView):
    model = Product
    template_name = 'product-details.html'
    slug_url_kwarg = 'id'
    slug_field = 'pk'
    context_object_name = 'product'

    def get_similar_products(self, product):
        result = re.sub(r'\b\w{1,5}\b', '', product.name)
        cleaned_text = re.sub(r'[^\w\s]', ' ', result)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        search_obj = SearchFilter(Product.objects.all(), ['name__iregex',], f"['{cleaned_text}']")
        qs = search_obj.get_filtered_qs(search_obj.apply_filter())
        return qs.exclude(pk=product.id), Price.objects.available_prices(qs)

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        similar_products, similar_products_prices = self.get_similar_products(context['product'])

        return context | {
            'prices'                 : Price.objects.available_prices(
                Product.objects.filter(pk=context['product'].id)
            ),
            'cart'                   : Cart(self.request),
            'similar_products'       : similar_products,
            'similar_products_prices': similar_products_prices,
            'MEDIA_URL'              : settings.MEDIA_URL
        }


def get_or_update_category(data):
    category_data = dict(data.pop('category'))
    serializer = CategorySerializer(instance='', data=[category_data], many=True)
    if serializer.is_valid():
        return first(serializer.save(), Category.objects.none())

    return Category.objects.none()


def get_or_update_product(data):
    product_data = dict(data.pop('product'))
    category = get_or_update_category(product_data)
    product, _ = Product.objects.update_or_create(
        identifier_1C=product_data.get('identifier_1C', ''),
        category=category, defaults = product_data
    )
    return product


class Base64ImageField(ImageField):
    
    def to_representation(self, value):
        '''Этот метод используется для преобразования изображения в строку Base64
        при сериализации. Он читает файл изображения и кодирует его в Base64, 
        добавляя MIME-тип в начале'''

        if not value:
            return None

        with open(value.path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        
        mime_type, _ = mimetypes.guess_type(value.path)
        if mime_type is None:
            mime_type = "application/octet-stream"

        return f"data:{mime_type};base64,{encoded_string}"
    

    def to_internal_value(self, data):
        '''Этот метод преобразует строку Base64 обратно 
        в файл изображения при десериализации.'''

        if isinstance(data, six.string_types):
            if 'data:' in data and ';base64,' in data:
                _, data = data.split(';base64,')

            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            file_name = self.get_file_name(decoded_file)
            file_extension = self.get_file_extension(file_name, decoded_file)

            complete_file_name = "%s.%s" % (file_name, file_extension)
            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)


    def get_file_extension(self, file_name, decoded_file):
        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension
        return extension


    def get_file_name(self, decoded_file):
        return "uploaded_image"


class CategoryListSerializer(ListSerializer):

    def update(self, instance, validated_data):
        ret = []
        for item in validated_data:
            with suppress(KeyError, IndexError):
                categories = self.update(
                    instance, [dict(item.pop('parent_category'))]
                )
                item = item | {'parent_category': categories[0]}    
            category, _ = Category.objects.update_or_create(
                identifier_1C=item.pop('identifier_1C', ''),
                name=item.pop('name', ''),
                defaults = item
            )
            ret.append(category)
        return ret


class CategorySerializer(ModelSerializer):
    parent_category = RecursiveField(required=False)
    
    class Meta:
        model = Category
        fields = ['name', 'identifier_1C', 'parent_category']
        list_serializer_class = CategoryListSerializer


class ProductListSerializer(ListSerializer):

    def update(self, _, validated_data):
        ret = []
        for item in validated_data:
            category = get_or_update_category(item)
            product, _ = Product.objects.update_or_create(
                identifier_1C=item['identifier_1C'],
                category=category,
                defaults = item
            )
            ret.append(product)
        return ret

    def create(self, validated_data):
        products = [Product(**item) for item in validated_data]
        return Product.objects.bulk_create(products)


class ProductSerializer(ModelSerializer):

    category = CategorySerializer()

    class Meta:
        model = Product
        fields = '__all__'
        list_serializer_class = ProductListSerializer


class ProductImageListSerializer(ListSerializer):

    def update(self, _, validated_data):
        ret = []
        for item in validated_data:
            product = get_or_update_product(item)
            product_image, _ = ProductImage.objects.update_or_create(
                product = product,
                defaults = item
            )
            ret.append(product_image)
            
        return ret


class ProductImageSerializer(ModelSerializer):

    product = ProductSerializer()
    image = Base64ImageField()

    class Meta:
        model = ProductImage
        fields = '__all__'
        list_serializer_class = ProductImageListSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_categories(request):
    serializer = CategorySerializer(instance='', data=request.data, many=True)
    if serializer.is_valid():
        serializer.save()
        return Response('success upload', status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_products(request):
    serializer = ProductSerializer(instance='', data=request.data, many=True)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response('success upload', status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_images(request):
    serializer = ProductImageSerializer(instance='', data=request.data, many=True)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response('success upload', status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
