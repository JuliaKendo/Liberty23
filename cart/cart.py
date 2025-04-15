from decimal import Decimal
from django.conf import settings
from contextlib import suppress
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework_recursive.fields import RecursiveField

from catalog.models import Category, Product
from enterprise.models import EnterpriseSetting

class BasketOverWeight(BaseException):

    def __str__(self):
        return 'Превышен допустимый вес корзины.'
    

class QuantityOverStock(BaseException):

    def __str__(self):
        return 'Недостаточно остатка на складе.'


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
            'weight',
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

    def check_cart(self, product, quantity, update):
        product_id = str(product.id)
        if self.cart.get(product_id):
            quantity_in_cart = self.cart[product_id]['quantity']
            if update:
                quantity_in_cart += quantity
            else:
                quantity_in_cart = quantity
            weight_products = sum(
                float(item['product']['weight']) * \
                    quantity_in_cart if item['product']['id'] == product.id else item['quantity'] \
                    for item in self.cart.values()
            )
        else:
            quantity_in_cart = quantity
            weight_products = sum(
                float(item['product']['weight']) * item['quantity'] for item in self.cart.values()) \
                    + (quantity_in_cart * float(product.weight)
            )
        if quantity_in_cart > product.stock:
            raise QuantityOverStock
        weight_limit = self.get_weight_limit()  
        if weight_limit and weight_limit < weight_products:
            raise BasketOverWeight


    def get_total_price(self):
        return sum(float(item['price']) * item['quantity'] for item in self.cart.values())

    def get_total_weight(self):
        return sum(float(item['product']['weight']) * item['quantity'] for item in self.cart.values())

    def get_weight_limit(self):
        with suppress(EnterpriseSetting.DoesNotExist):
            enterprise_setting = EnterpriseSetting.objects.first()
            return enterprise_setting.max_cart_weght

    def add(self, product, quantity=1, price=0, update_quantity=False):
        product_id = str(product.id)
        with suppress(Product.DoesNotExist):
            current_product = Product.objects.get(id=product_id)
            self.check_cart(current_product, quantity, update_quantity)
            if product_id not in self.cart:
                self.cart[product_id] = {
                    'product': ProductSerializer(current_product).data,
                    'quantity': 0,
                    'price': str(price)
                }
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
                    'weight': float(Product.objects.get(id=k).weight * v['quantity']),
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
                'weight': float(Product.objects.get(id=k).weight * v['quantity']),
                'price': float(v['price']),
                'total_price': float(Decimal(v['price']) * v['quantity']),
                'update': 1
            } for k, v in self.cart.items()
        ]

