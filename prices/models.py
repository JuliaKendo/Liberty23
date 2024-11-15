from django.db import models
from contextlib import suppress
from django.core.validators import MinValueValidator
from django.db.models import Q, Max
from django.utils import timezone

from enterprise.models import Department
from catalog.models import Product


class PriceType(models.Model):
    name = models.CharField('Наименование', max_length=100, db_index=True)

    class Meta:
        verbose_name = 'Тип цены'
        verbose_name_plural = 'Типы цен'

    def __str__(self):
        return self.name


class PriceQuerySet(models.QuerySet):
    
    def available_prices(self, products, price_type = None):
        with suppress(PriceType.DoesNotExist):
            if not price_type:
                price_type = PriceType.objects.get(name='Базовая')   
            return self.distinct().filter(
                type=price_type,
                product__in=products,
                start_at__lte=timezone.now()
            ).filter(
                Q(end_at__isnull=True) | Q(end_at__gte=timezone.now())
            ).annotate(actual_price=Max('price'))
        return self.all()


class Price(models.Model):
    type = models.ForeignKey(
        PriceType,
        on_delete=models.CASCADE,
        verbose_name='Тип цены',
        related_name='prices',
        db_index=True,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Номенклатура',
        related_name='product_prices',
        db_index=True,
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
    price = models.DecimalField(
        'Цена',
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
    start_at = models.DateTimeField(
        'Дата начала действия', db_index=True, default=timezone.now
    )
    end_at = models.DateTimeField(
        'Дата окончания действия', db_index=True, blank=True,null=True
    )

    objects = PriceQuerySet.as_manager()

    class Meta:
        verbose_name = 'Цена'
        verbose_name_plural = 'Цены'

    def __str__(self):
        return f'{self.product} {self.price} руб ({self.type})'


class DeliveryPriceQuerySet(models.QuerySet):
    
    def available_delivery_price(self, department):
        with suppress(PriceType.DoesNotExist): 
            return self.distinct().filter(
                department_id=department.id,
                start_at__lte=timezone.now()
            ).filter(
                Q(end_at__isnull=True) | Q(end_at__gte=timezone.now())
            ).annotate(actual_price=Max('price'))
        return self.all()


class DeliveryPrice(models.Model):

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        verbose_name='Подразделение',
        related_name='department_prices',
        db_index=True,
    )
    price = models.DecimalField(
        'Цена',
        max_digits=8,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    start_at = models.DateTimeField(
        'Дата начала действия', db_index=True, default=timezone.now
    )
    end_at = models.DateTimeField(
        'Дата окончания действия', db_index=True, blank=True,null=True
    )

    objects = DeliveryPriceQuerySet.as_manager()

    class Meta:
        verbose_name = 'Цена доставки'
        verbose_name_plural = 'Цены доставки'

    def __str__(self):
        return f'{self.department} - {self.price} руб.'
