from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import OutgoingMail, MailingOfLetters, NotifyTemplate, Emails
from .tasks import launch_mailing, get_email_addresses, create_outgoing_mail


class EmailsInLine(admin.TabularInline):
    model = Emails
    extra = 0
    fields = ('mailing_of_letter', 'email',)
    classes = ('collapse', )

    verbose_name = 'Email'
    verbose_name_plural = 'Emails'


@launch_mailing()
def send_outgoing_mail(patams):
    return OutgoingMail.objects.get(id=patams['id'])


class OutgoingMailSentFilter(admin.SimpleListFilter):
    title = ('Статус письма')
    parameter_name = 'sent'

    def lookups(self, request, model_admin):
        return (
            ('sent', ('Отправленные')),
            ('unsent', ('Не отправленные')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'sent':
            return queryset.exclude(sent_date__isnull=True)
        if self.value() == 'unsent':
            return queryset.filter(sent_date__isnull=True)


@admin.register(NotifyTemplate)
class NotifyTemplateAdmin(SummernoteModelAdmin):
    search_fields = ['name', ]
    list_display = ['name', ]
    summernote_fields = ('header_template', 'footer_template',)
    fields = ['name', 'header_template', 'footer_template',]

    def has_module_permission(self, request):
        return False


@admin.register(OutgoingMail)
class OutgoingMailAdmin(SummernoteModelAdmin):
    search_fields = ['email', 'subject']
    list_display = ['email', 'subject', 'sent_date',]
    summernote_fields = ('html_content',)
    list_filter = [OutgoingMailSentFilter,]
    list_display_links = ('email', 'subject',)

    fields = ['email', 'subject', 'html_content',]

    actions = ['put_in_mail_queue']
    @admin.action(description='Поместить в очередь отправки')
    def put_in_mail_queue(self, request, queryset):
        for obj in queryset:
            send_outgoing_mail({'id': obj.id})


@admin.register(MailingOfLetters)
class MailingOfLettersAdmin(SummernoteModelAdmin):
    readonly_fields = []
    search_fields = ['name', 'status']
    list_display = ['created_at', 'name', 'status', 'subject',]
    summernote_fields = ('content',)
    list_filter = ['status',]
    list_display_links = ('created_at', 'name', 'status', 'subject')
    fields = ['name', 'subject', 'content', 'template', ]

    inlines = [EmailsInLine,]

    actions = ['set_sent_status']
    @admin.action(description='Установить статус к отправке')
    def set_sent_status(self, request, queryset):
        for obj in queryset:
            email_addresses = get_email_addresses(
                Emails.objects.all().prefetch_related('emails').filter()    
            )
            if not email_addresses: continue
            obj.status=MailingOfLetters.SENT
            obj.save(update_fields=['status'])
            create_outgoing_mail({
                'recipient_list'   : list(set(email_addresses)),
                'subject'          : obj.subject,
                'template'         : obj.template,
                'content'          : obj.content,
                'context'          : {},
                'mailing_of_letter': obj,
            })


    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status != MailingOfLetters.NEW:
            return list(self.readonly_fields) + \
            [field.name for field in obj._meta.fields] + \
            [field.name for field in obj._meta.many_to_many]
        return self.readonly_fields


    def get_inline_instances(self, request, obj=None):
        inline_instances = []
        for inline_class in self.inlines:
            if self.should_show_inline(request, obj, inline_class):
                inline = inline_class(self.model, self.admin_site)
                inline_instances.append(inline)
        return inline_instances
    

    def should_show_inline(self, request, obj, inline_class):
        if not obj:
            return True
        if obj.status == MailingOfLetters.NEW:
            return True
        return False
    

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if not 'segment' in fields:
            fields.append('segment')    
        if not obj and 'segment' in fields:
            fields.remove('segment')
        elif obj and obj.status == MailingOfLetters.NEW and 'segment' in fields:
            fields.remove('segment')
        return fields


    def has_module_permission(self, request):
        return False
