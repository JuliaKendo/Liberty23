from django.contrib import admin
from django.utils.html import format_html
from django_summernote.admin import SummernoteModelAdmin

from .models import Contacts, News


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

