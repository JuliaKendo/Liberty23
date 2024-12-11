from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django_summernote.admin import SummernoteModelAdmin

from .models import Contacts, News, Department, PaymentSetup
from prices.models import DeliveryPrice


class DeliveryPriceInLine(admin.TabularInline):
    model = DeliveryPrice
    extra = 0
    fields = ('department', 'price', 'start_at', 'end_at')
    readonly_fields = ('start_at',)
    classes = ('collapse', )

    verbose_name = 'Цена доставки'
    verbose_name_plural = 'Цены доставки'


@admin.register(Contacts)
class ContactsAdmin(admin.ModelAdmin):
    search_fields = [
        'name',
    ]
    list_display = [
        'name',
        'phone',
        'email',
        'address',
        'fax',
        'insta',
        'vk'
    ]
    fields = [
        'name',
        ('phone', 'additional_phone', 'fax',),
        ('email', 'additional_email',),
        'address',
        ('insta', 'ok', 'fb', 'vk',),
    ]
    list_display_links = list_display


@admin.register(News)
class NewsAdmin(SummernoteModelAdmin):
    search_fields = ['title',]
    list_display = ['render_preview', 'title', 'created_at',]
    summernote_fields = ('content',)
    fields = ['title', 'picture', 'content', 'created_at',]
    readonly_fields = ('render_preview', 'created_at',)

    list_display_links = list_display

    def render_preview(self, obj):
        if obj.picture:
            return format_html(
                '<img src="{0}" width="50" height="50" />'.format(obj.picture.url)
            )
        else:
            return '(No image)'

    render_preview.short_description = 'Preview'


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    search_fields = ['name',]
    list_display = ['name',]
    fields = ['name',]
    list_display_links = list_display

    inlines = [DeliveryPriceInLine,]


class PasswordInputForm(forms.ModelForm):
    class Meta:
        model = PaymentSetup
        fields = '__all__'
        widgets = {
            'password1': forms.PasswordInput(),
            'password2': forms.PasswordInput(),
        }


@admin.register(PaymentSetup)
class PaymentSetupAdmin(admin.ModelAdmin):
    form = PasswordInputForm

    search_fields = []
    list_display = ['name', 'merchant_login',]
    fields = [
        'name',
        'merchant_login',
        ('password1', 'password2'),
        'is_test',
    ]
    list_display_links = list_display
