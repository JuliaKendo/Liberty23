from django.contrib import admin
from django.db.models import Sum
from django.contrib import admin
from django import forms

from .models import Order, OrderItem, DeliveryAddresses


class CustomOrderItemForm(forms.ModelForm):

    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    form = CustomOrderItemForm
    readonly_fields = (
        'articul',
        'unit',
    )
    fields = [
        'articul',
        'product',
        'quantity',
        'unit',
        'sum',
    ]
    classes = ('hide-title',)
    extra = 0
    verbose_name = "Номенклатура"
    verbose_name_plural = "Номенклатура"

    def articul(self, obj):
        return obj.product.articul
    articul.short_description = 'Артикул'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    search_fields = [
        'id',
    ]
    list_display = [
        'id',
        'created_at',
        'status',
        'department',
        'customer',
        'delivery_address',
        'order_sum',
    ]
    list_display_links = list_display
    list_filter = ['status',]
    fields = [
        'created_at',
        'status',
        'department',
        'customer',
        'delivery_address',
        'additional_info',
    ]
    ordering = ('id', 'created_at')
    readonly_fields = ['order_sum','created_at',]
    inlines = [OrderItemInline]

    def order_sum(self, obj):
        result = OrderItem.objects.filter(order=obj).aggregate(Sum('sum'))
        return result['sum__sum']
    order_sum.short_description = 'Сумма'


@admin.register(DeliveryAddresses)
class DeliveryAddressesAdmin(admin.ModelAdmin):
    search_fields = ['fname', 'lname', 'email']
    list_display = [
        'customer',
        'fname',
        'lname',
        'patronymic',
        'date_of_birth',
        'email',
    ]
    list_display_links = list_display
    list_filter = ['fname', 'lname', 'date_of_birth', 'email']
    fields = [
        ('customer', 'created_at',),
        'fname',
        'lname',
        'patronymic',
        'date_of_birth',
        'company',
        'address',
        'country',
        'town',
        'state',
        'zip',
        'email',
        'phone',
    ]
    readonly_fields = ['created_at',]
