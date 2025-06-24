from django.db import models
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField

from django.contrib.auth.models import User
from enterprise.models import Department
from catalog.models import Product
from prices.models import PriceType


class DeliveryAddresses(models.Model):
    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Покупатель',
        related_name='user_delivery_addresses',
        db_index=True,
    )
    country    = models.CharField('Страна доставки', max_length=50, blank=True)
    fname      = models.CharField('Имя', max_length=50, blank=True)
    lname      = models.CharField('Фамилия', max_length=100, blank=True)
    company    = models.CharField('Компания', max_length=100, blank=True)
    address    = models.CharField('Адрес', max_length=200, blank=True)
    town       = models.CharField('Город', max_length=50, blank=True)
    state      = models.CharField('Область / Край', max_length=50, blank=True)
    zip        = models.CharField('Индекс', max_length=6, blank=True)
    email      = models.EmailField('email', blank=True)
    phone      = PhoneNumberField('Контактный телефон', blank=True)
    created_at = models.DateTimeField('Дата создания', db_index=True, auto_now_add=True)
    date_of_birth = models.DateField('Дата рождения', blank=True, null=True)

    class Meta:
        verbose_name = 'Адрес доставки'
        verbose_name_plural = 'Адреса доставки'

    def __str__(self):
        return f'{self.lname} {self.fname} ({self.email})'


class Order(models.Model):
    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Покупатель',
        related_name='user_oders',
        db_index=True,
    )
    status = models.CharField(
        'Статус',
        max_length=20,
        default='introductory',
        db_index=True,
        choices=(
            ('introductory', 'Предварительный'),
            ('confirmed'   , 'Подтвержден'),
            ('paid'        , 'Оплачен'),
            ('shipment'    , 'Отгрузка'),
            ('completed'   , 'Завершен'),
    ))
    delivery_address = models.ForeignKey(
        DeliveryAddresses,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Адрес доставки',
        related_name='address_oders',
        db_index=True,
    )
    additional_info = models.TextField('Дополнительная информация', blank=True)
    created_at = models.DateTimeField(
        'Дата создания', db_index=True, auto_now_add=True
    )
    identifier_1C = models.CharField(
        'Идентификатор 1С', max_length=50, blank=True, db_index=True
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        verbose_name='Подразделение',
        related_name='department_oders',
        blank=True,
        null=True,
        db_index=True,
    )

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'Заказ № {self.id} от {self.created_at.strftime("%d-%b-%Y %H:%M:%S")}'
    
    def get_total_cost(self):
        return sum(item.sum for item in self.items.all())
    
    def get_total_quantity(self):
        return sum(item.quantity for item in self.items.all())
    
    def get_total_weight(self):
        return sum(item.product.weight * item.quantity for item in self.items.all())

    def natural_key(self):
        return (self.id, self.created_at, )


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        db_index=True,
        verbose_name='Заказ',
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_index=True,
        verbose_name='Номенклатура',
        related_name='product_orders'
    )
    unit = models.CharField(
        'Единица измерения',
        max_length=20,
        default='грамм',
        db_index=True,
        choices=(
            ('796', 'штук'),
            ('163', 'грамм'),
            ('166', 'кг'),
    ))
    quantity = models.PositiveIntegerField('Количество', default=1)
    price = models.DecimalField(
        'Цена',
        max_digits=8,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    sum = models.DecimalField(
        'Сумма',
        max_digits=8,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    discount = models.DecimalField(
        'Скидка',
        max_digits=8,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    price_type = models.ForeignKey(
        PriceType,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Тип цены',
        related_name='price_type_orders',
        db_index=True,
    )

    def __str__(self):
        return f'{self.id}'

    def get_cost(self):
        return self.price * self.quantity
    
    def get_cost_without_discount(self):
        return (self.price * self.quantity) - self.discount
