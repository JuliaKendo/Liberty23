from decimal import Decimal
from django.conf import settings
from contextlib import suppress
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework_recursive.fields import RecursiveField

from catalog.models import Category, Product


class CategorySerializer(ModelSerializer):
    parent_category = RecursiveField(required=False)
    
    class Meta:
        model = Category
        fields = ['name', 'identifier_1C', 'parent_category']


class ProductSerializer(ModelSerializer):
    category = CategorySerializer()
    image = SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'articul',
            'category',
            'unit',
            'stock',
            'created_at',
            'product_type',
            'description',
            'image',
        ]

    def get_image(self, obj):
        return obj.get_image


class Cart(object):

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    
    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            self.cart[str(product.id)]['product'] = ProductSerializer(product).data

        for item in self.cart.values():
            item['price'] = float(item['price'])
            item['total_price'] = float(item['price'] * item['quantity'])
            yield item


    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())


    def get_total_price(self):
        return sum(float(item['price']) * item['quantity'] for item in self.cart.values())


    def add(self, product, quantity=1, price=0, update_quantity=False):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(price)}
        if update_quantity:
            self.cart[product_id]['quantity'] += quantity
        else:
            self.cart[product_id]['quantity'] = quantity
        self.save()


    def sub(self, product, quantity=1):
        product_id = str(product.id)
        if product_id in self.cart:
            self.cart[product_id]['quantity'] -= quantity
            self.save()


    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True


    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    
    def clear(self):
        # удаление корзины из сессии
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True


    def to_json(self, key=None):
        if key:
            return [
                {
                    **{'id': k},
                    'unit': Product.objects.get(id=k).unit,
                    'quantity': v['quantity'],
                    'total_quantity': sum(item['quantity'] for item in self.cart.values()),
                    'price': float(v['price']),
                    'total_price': float(Decimal(v['price']) * v['quantity']),
                    'update': 1
                } for k, v in self.cart.items() if k == key
            ]
        
        return [
            {
                **{'id': k},
                'unit': Product.objects.get(id=k).unit,
                'quantity': v['quantity'],
                'total_quantity': sum(item['quantity'] for item in self.cart.values()),
                'price': float(v['price']),
                'total_price': float(Decimal(v['price']) * v['quantity']),
                'update': 1
            } for k, v in self.cart.items()
        ]

