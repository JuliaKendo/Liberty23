import json

from random import choice
from string import digits, ascii_letters

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from django.contrib.auth import login
from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .models import DeliveryAddresses, Order, OrderItem
from .forms import OrderForm, OrderItemForm, DeliveryAddressesForm
from cart.cart import Cart
from catalog.models import Product
from prices.models import PriceType
from Liberty23.forms import SignUpForm


class CartIsEmpty(Exception):
    pass


class PriceTypeSerializer(ModelSerializer):

    class Meta:
        model = PriceType
        fields = ['name']


class ProductSerializer(ModelSerializer):

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'articul',
            'unit',
            'created_at',
            'description',
            'identifier_1C'
        ]


class OrderItemSerializer(ModelSerializer):

    product = ProductSerializer()
    price_type = PriceTypeSerializer()

    class Meta:
        model = OrderItem
        fields = '__all__'


class UserSerializer(ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = [
            'id',
            'is_superuser',
            'username',
            'is_active',
            'is_staff'
        ]


class DeliveryAddressSerializer(ModelSerializer):

    customer = UserSerializer()

    class Meta:
        model = DeliveryAddresses
        fields = '__all__'


class OrderSerializer(ModelSerializer):

    customer = UserSerializer()
    delivery_address = DeliveryAddressSerializer()

    class Meta:
        model = Order
        fields = '__all__'


class CheckoutView(TemplateView):
    template_name = 'checkout.html'

    def get_context_data(self, **kwargs): 
        context = super().get_context_data(**kwargs)
        context['delivery_addresses'] = DeliveryAddresses.objects.none()
        if self.request.user.is_authenticated:
            context['delivery_addresses'] = DeliveryAddresses.objects.filter(customer=self.request.user).order_by('-created_at')
        return context


def generate_password(length=6):
    s = ''
    for _ in range(length):
        s += choice(digits + ascii_letters)
    return s


def create_user_and_login(request, param):
    username = f'{param["fname"]}_{param["lname"]}'
    new_password = generate_password(8)
    form = SignUpForm({
        'username': username,
        'email': param['email'],
        'password1': new_password,
        'password2': new_password
    })
    if form.is_valid():
        user = form.save()
        login(request, user)
        return user
    raise ValidationError(form.errors)


@require_POST
def order_add(request):
    user = request.user
    cart = Cart(request)
    create_account = request.POST.get('createAccount', '') == 'on' \
        and not request.user.is_authenticated
    delivery_addresses_form = DeliveryAddressesForm(request.POST)
    delivery_addresses_instance = DeliveryAddresses.objects.none()

    try:
        if not len(cart):
            raise CartIsEmpty; 
        with transaction.atomic(): 
            if delivery_addresses_form.is_valid():
                if create_account:
                    user = create_user_and_login(request, delivery_addresses_form.cleaned_data)

                delivery_addresses_instance = delivery_addresses_form.save(commit=False)
                delivery_addresses_instance.customer = user
                delivery_addresses_instance.save()
                order_form = OrderForm({
                    'customer': user,
                    'status': 'introductory',
                    'delivery_address': delivery_addresses_instance,
                    'additional_info': request.POST.get('additional_info', ''),
                })
                if order_form.is_valid():
                    errors = []
                    order_instance = order_form.save(commit=False)
                    order_instance.save()
                    for item in cart:
                        product = Product.objects.get(pk=item['product']['id'])
                        item_form = OrderItemForm({
                            'product': product,
                            'unit': product.unit,
                            'quantity': item['quantity'],
                            'price': item['price'],
                            'sum': item['total_price']
                        })
                        if item_form.is_valid():
                            item_instance = item_form.save(commit=False)
                            item_instance.order = order_instance
                            item_instance.save()
                        else:
                            errors.append(order_form.errors)
                            continue
                    if errors:
                        raise ValidationError(errors)
                else:
                    raise ValidationError(order_form.errors)
            else:
                raise ValidationError(delivery_addresses_form.errors)

    except ValidationError as errors:
        transaction.rollback()
        return JsonResponse(errors.message_dict, safe=False)
    
    except ValueError as errors:
        transaction.rollback()
        return JsonResponse(
            {
                'createAccount': ['Для оформелния заказа необходимо войти или зарегистрироваться.']
            },
            safe=False
        )

    except CartIsEmpty as errors:
        transaction.rollback()
        return JsonResponse(
            {'cartIsEmpty': ['В корзине отсутствуют товары для заказа']},
            safe=False
        )       

    finally:
        if transaction.get_autocommit():
            transaction.commit()
            cart.clear()

    return JsonResponse({}, status=200)


@require_POST
def order_remove(request, order_id):...


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def unload_orders(request, *args, **kwargs):
    period = {}
    if kwargs.get('data_from'):
        period['created_at__gte'] = kwargs['data_from']
    if kwargs.get('data_to'):
        period['created_at__lte'] = kwargs['data_to']  
    serialized_orders = []
    for order in Order.objects.filter(**period):
        serialized_order = json.loads(json.dumps(OrderSerializer(order).data))
        serialized_order['products'] = json.loads(
            json.dumps(
                OrderItemSerializer(OrderItem.objects.filter(order_id=order.id), many=True).data
        ))
        serialized_orders.append(serialized_order)

    return JsonResponse(serialized_orders, status=200, safe=False)
