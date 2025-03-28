from django.contrib import admin

from .models import Price, PriceType, DeliveryPrice


@admin.register(PriceType)
class PriceTypeAdmin(admin.ModelAdmin):
    list_display = [
        'name',
    ]
    fields = [
        'name',
    ]


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    search_fields = [
        'type__name',
        'product__name',
        'product__articul',
    ]
    list_display = [
        'type',
        'product',
        'unit',
        'price',
        'discount',
        'start_at',
        'end_at',
    ]
    fields = [
        'type',
        'product',
        'unit',
        'price',
        'discount',
        'start_at',
        'end_at',
    ]
    list_filter = [
        'type',
        'product',
    ]
    readonly_fields = [
        'start_at',
    ]

    list_display_links = fields


@admin.register(DeliveryPrice)
class DeliveryPriceAdmin(admin.ModelAdmin):
    search_fields = ['department__name',]
    list_display = [
        'department',
        'price',
        'start_at',
        'end_at',
    ]
    fields = [
        'department',
        'price',
        'start_at',
        'end_at',
    ]
    list_filter = [
        'department',
    ]
    readonly_fields = [
        'start_at',
    ]

    list_display_links = fields
