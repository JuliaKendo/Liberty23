import json

from random import choice
from string import digits, ascii_letters

from django.conf import settings
from django.db import transaction
from django.db.models import Sum
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView, TemplateView
from django.views.decorators.http import require_POST, require_GET
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.core.exceptions import ValidationError
from django.contrib.auth import login
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from contextlib import suppress
from rest_framework.serializers import ModelSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .models import DeliveryAddresses, Order, OrderItem
from .forms import OrderForm, OrderItemForm, DeliveryAddressesForm
from .tasks import planed_update_of_stoks, send_by_email
from cart.cart import Cart
from cart.models import Basket
from catalog.models import Product
from prices.models import PriceType
from Liberty23.forms import SignUpForm
from prices.lib import get_delivery_price
from enterprise.models import Department
from enterprise.departments import СurrentDepartment


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


class DepartmentSerializer(ModelSerializer):

    class Meta:
        model = Department
        fields = '__all__'


class OrderSerializer(ModelSerializer):

    customer = UserSerializer()
    delivery_address = DeliveryAddressSerializer()
    department = DepartmentSerializer()

    class Meta:
        model = Order
        fields = '__all__'


class OrdersView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders.html'
    context_object_name = 'orders'
    allow_empty = True
    paginate_by = 10
    login_url = '/'

    def get_queryset(self):
        department_instance = СurrentDepartment(self.request)
        queryset = Order.objects.filter(
            department=department_instance.department,
            customer=self.request.user
        ).exclude(status='completed').order_by('-created_at')
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        self.object_list = self.get_queryset()
        context = super().get_context_data(**kwargs)

        paginator = Paginator(context['orders'], self.paginate_by)
        page = self.request.GET.get('page')
        
        try:
            order_page = paginator.page(page)
        except PageNotAnInteger:
            order_page = paginator.page(1)
        except EmptyPage:
            order_page = paginator.page(paginator.num_pages)

        context['orders']  = order_page
        context['MEDIA_URL'] = settings.MEDIA_URL
    
        return context


class CheckoutView(LoginRequiredMixin, TemplateView):
    template_name = 'checkout.html'
    login_url = '/'

    def get_context_data(self, **kwargs): 
        context = super().get_context_data(**kwargs)
        context['delivery_addresses'] = DeliveryAddresses.objects.none()
        context['delivery_price'] = 0
        if self.request.user.is_authenticated:
            context['delivery_addresses'] = DeliveryAddresses.objects.filter(customer=self.request.user).order_by('-created_at')
            context['delivery_price'] = get_delivery_price(self.request)
        context['order'] = Order.objects.none()
        context['ready_for_payment'] = True
        context['read_only'] = False
        return context


class PreOrderView(CheckoutView):
    def _sync_cart_to_basket(self, user, cart):
        """
        Переносит содержимое корзины (Cart) в Basket пользователя.
        Если товар уже есть в Basket — обновляет количество и сумму.
        Если нет — добавляет новые записи (bulk_create для оптимизации).
        """
        new_items = []

        for item in cart:
            product = get_object_or_404(Product, pk=item['product']['id'])
            basket_item = Basket.objects.filter(
                user=user, product=product, unit=product.unit
            ).first()

            if basket_item:
                basket_item.quantity += item['quantity']
                basket_item.price = item['price']
                basket_item.sum = float(basket_item.sum) + item['total_price']
                basket_item.save(update_fields=["quantity", "price", "sum"])
            else:
                new_items.append(
                    Basket(
                        user=user, product=product,
                        unit=product.unit, quantity=item['quantity'],
                        price=item['price'], sum=item['total_price']
                    )
                )

        if new_items:
            Basket.objects.bulk_create(new_items)

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        cart = Cart(request)
        try:
            with transaction.atomic():
                self._sync_cart_to_basket(user, cart)

        except Exception:
            # Если ошибка — транзакция автоматически откатится
            return super().dispatch(request, *args, **kwargs)
        else:
            cart.clear()

        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs): 
        context = super().get_context_data(**kwargs)
        context['basket'] = []
    
        user = self.request.user
        if user:
            context['basket'] = Basket.objects.filter(user=user).annotate(sum__sum=Sum('sum'))
        context['read_only'] = False

        return context


class OrderView(CheckoutView):
    def get_context_data(self, **kwargs): 
        context = super().get_context_data(**kwargs)
        order_id = kwargs.get('order_id')
        if not order_id:
            return context
        
        context['ready_for_payment'] = False
        context['order'] = get_object_or_404(Order, pk=order_id)
        context['basket'] = OrderItem.objects.filter(order__pk=order_id)
        context['read_only'] = True
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


def remove_from_basket(request, product_id):
    user = request.user
    product = get_object_or_404(Product, id=product_id)
    Basket.objects.filter(user=user, product=product).delete()
    return redirect('orders:pre-order')


@require_POST
@planed_update_of_stoks()
@send_by_email()
def order_add(request):
    user = request.user
    cart = Basket.objects.filter(user=user)
    if not len(cart): 
        JsonResponse({'cartIsEmpty': ['В корзине отсутствуют товары для заказа']}, status=400)
    
    create_account = request.POST.get('createAccount', '') == 'on' \
        and not request.user.is_authenticated

    delivery_addresses_form = DeliveryAddressesForm(request.POST)
    if not delivery_addresses_form.is_valid():
        return JsonResponse(delivery_addresses_form.errors, status=400)

    try:  
        with transaction.atomic(): 
            # Получаем или создаем адрес доставки
            if create_account:
                user = create_user_and_login(request, delivery_addresses_form.cleaned_data)
            delivery_address = _get_or_update_delivery_address(user, delivery_addresses_form)

            # Создаем заказ
            order = _create_order(request, user, delivery_address)

            # Добавляем позиции заказа
            _create_order_items(order, cart)

            # Очищаем корзину
            cart.delete()


    except ValidationError as errors:
        return JsonResponse(errors.message_dict, safe=False)
    
    except ValueError as errors:
        return JsonResponse(
            {
                'createAccount': ['Для оформелния заказа необходимо войти или зарегистрироваться.']
            },
            safe=False
        )

    return JsonResponse({'InvId': order.id}, status=200)


def _get_or_update_delivery_address(user, delivery_form):
    """Получает или обновляет адрес доставки для пользователя."""
    try:
        delivery_address = DeliveryAddresses.objects.get(customer=user)
        delivery_address.__dict__.update(
            **{
                key: value for \
                key, value in \
                delivery_form.cleaned_data.items() if key in [
                    'country', 'fname', 'lname', 'patronymic',
                    'company', 'address', 'town', 'state', 'zip',
                    'email', 'phone', 'date_of_birth'
        ]})
    except DeliveryAddresses.DoesNotExist:
        delivery_address = delivery_form.save(commit=False)
        delivery_address.customer = user
    delivery_address.save()
    return delivery_address


def _create_order(request, user, delivery_address):
    """Создает заказ для пользователя."""
    order_form = OrderForm({
        'customer': user,
        'status': request.POST.get('status', 'introductory'),
        'delivery_address': delivery_address,
        'additional_info': request.POST.get('additional_info', ''),
        'department': СurrentDepartment(request).department
    })

    if not order_form.is_valid():
        raise ValidationError(order_form.errors)

    return order_form.save()


def _create_order_items(order, cart):
    """Создает позиции заказа на основе корзины."""
    errors = []
    for item in cart:
        item_form = OrderItemForm({
            'product': item.product,
            'unit': item.unit,
            'quantity': item.quantity,
            'price': item.price,
            'sum': item.sum,
        })
        if item_form.is_valid():
            order_item = item_form.save(commit=False)
            order_item.order = order
            order_item.save()
        else:
            errors.append(item_form.errors)

    if errors:
        raise ValidationError(errors)


@require_GET
def order_remove(request, order_id=None):
    def get_last_order_id():
        last_order = Order.objects.filter(
            customer= request.user,
            status='introductory'
        ).order_by('-created_at').first()
        if last_order: 
            return last_order.id

    if not order_id:
        order_id = get_last_order_id()

    if order_id:
        basket = []
        order = get_object_or_404(Order, pk=order_id)
        order_items = OrderItem.objects.filter(order=order)
        for order_item in order_items:
            basket.append(
                Basket(
                    user=request.user,
                    product=order_item.product,
                    unit=order_item.unit,
                    quantity=order_item.quantity,
                    price=order_item.price,
                    sum=order_item.sum
            ))
        try:
            with transaction.atomic(): 
                Order.objects.filter(pk=order_id).delete()
                if order.status == 'introductory':
                    Basket.objects.bulk_create(basket)
        finally:
            if transaction.get_autocommit():
                transaction.commit()

    return redirect('orders:list')


@require_GET
def handle_result_payment(request, *args, **kwargs):
    result = request.GET.dict()
    if result and result.get('InvId') and result.get('IncSum'):
        order = get_object_or_404(Order, pk=result.get('InvId'))
        order.status = 'paid'
        order.save()
    return HttpResponse('')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def unload_orders(request, *args, **kwargs):
    if kwargs.get('order_id'):
        order = get_object_or_404(Order, pk=kwargs['order_id'])
        serialized_order = json.loads(json.dumps(OrderSerializer(order).data))
        serialized_order['products'] = json.loads(
            json.dumps(
                OrderItemSerializer(OrderItem.objects.filter(order_id=order.id), many=True).data
        ))
        return JsonResponse(serialized_order, status=200, safe=False)

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
 

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_order(request, *args, **kwargs):
    order_id = request.query_params.get('id')
    order_status = request.query_params.get('status')

    with suppress(ValidationError):
        if order_id and order_status:
            order = Order.objects.filter(id=order_id)
            if not order:
                raise ValidationError   
            order.update(**{
                'status': order_status,
            })
        else:
            raise ValidationError
        return JsonResponse(
            {'replay': 'ok'},
            status=200,
            safe=False,
            json_dumps_params={'ensure_ascii': False}
        )

    return JsonResponse(
        {'replay': 'error', 'message': 'Не найден заказ'},
        status=400,
        safe=False,
        json_dumps_params={'ensure_ascii': False}
    )
