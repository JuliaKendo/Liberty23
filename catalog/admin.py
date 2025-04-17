from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Product, ProductImage
from prices.models import Price

class DepartmentInLine(admin.TabularInline):
    model = Product.departments.through
    extra = 0
    verbose_name = 'Подразделение'
    verbose_name_plural = 'Подразделения'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'departments':
            product = Product.objects.get(pk=request.resolver_match.kwargs['object_id'])
            kwargs['queryset'] = product.departments.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ProductImageInLine(admin.TabularInline):
    model = ProductImage
    extra = 0
    fields = ('render_preview', 'image', 'filename',)
    readonly_fields = ('render_preview',)
    classes = ('collapse', )

    verbose_name = "Фотография"
    verbose_name_plural = "Фотографии"

    def render_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{0}" width="50" height="50" />'.format(obj.image.url)
            )
        else:
            return '(No image)'

    render_preview.short_description = 'Preview'


class PriceInLine(admin.TabularInline):
    model = Price
    extra = 0
    fields = ('type', 'product', 'unit', 'price', 'discount', 'start_at', 'end_at')
    readonly_fields = ('start_at',)
    classes = ('collapse', )

    verbose_name = 'Цена'
    verbose_name_plural = 'Цены'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = [
        'name',
    ]
    list_display = [
        'parent_category',
        'name',
    ]
    fields = [
        'parent_category',
        'name',
    ]
    list_filter = [
        'name',
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    search_fields = [
        'name',
        'articul',
    ]
    list_display = [
        'image_icon',
        'category',
        'articul',
        'name',
        'unit',
        'stock',
        'weight',
        'price'
    ]
    fields = [
        'image_tag',
        'product_type',
        'category',
        'articul',
        'name',
        'unit',
        ('stock', 'weight'),
        'description',
        'created_at',
    ]
    list_filter = [
        'category',
        'product_type',
        'unit'
    ]
    readonly_fields = [
        'image_tag',
        'created_at',
        'stock',
    ]
    inlines = [
        DepartmentInLine,
        ProductImageInLine,
        PriceInLine,
    ]
    list_display_links = [
        'category',
        'articul',
        'name',
        'unit'
    ]

    def price(self, obj):
        result = 0
        available_prices = Price.objects.available_prices([obj.id,])
        if available_prices:
            result = available_prices.first().price
        return result
    price.short_description = 'Цена, руб'

    def image_icon(self, obj):
        img = ProductImage.objects.filter(product_id=obj.id).first()
        if img:
            return format_html(
                '<img src="{0}" width="50" height="50" />'.format(img.image.url)
            )
    image_icon.short_description = '.'

    def image_tag(self, obj):
        img = ProductImage.objects.filter(product_id=obj.id).first()
        return format_html(
            '<img src="{0}" width="150" height="150" />'.format(img.image.url)
        )
    image_tag.short_description = 'Изображение'

