from django.db import models
from django.contrib.auth.models import User


class NotifyTemplate(models.Model):
    name = models.CharField('Наименование', max_length=150, unique=True)
    header_template = models.TextField('Заголовок письма', blank=True)
    footer_template = models.TextField('Подвал письма' , blank=True)

    class Meta:
        verbose_name = 'Шаблон письма'
        verbose_name_plural = 'Шаблоны писем'

    def __str__(self):
        return self.name



class MailingOfLetters(models.Model):
    COMPLETED  = 'completed'
    SENT       = 'sent'
    NEW        = 'new'

    STATUS_CHOICES = (
        (COMPLETED, 'Выполнено'),
        (SENT     , 'К отправке'),
        (NEW      , 'Новая'),
    )

    name = models.CharField('Наименование рассылки', max_length=150, unique=True)
    subject = models.CharField('Тема рассылки', max_length=100, blank=True)
    template = models.ForeignKey(
        NotifyTemplate,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Шаблон письма',
        related_name='mailing_of_letter_templates'
    )
    content = models.TextField('Содержание письма', blank=True)
    status = models.CharField(
        'Статус рассылки',
        max_length=20,
        db_index=True,
        default=NEW,
        choices=STATUS_CHOICES)
    created_at = models.DateTimeField(
        'Дата создания', db_index=True, auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'

    def __str__(self):
        return self.name


class Emails(models.Model):
    mailing_of_letter = models.ForeignKey(
        MailingOfLetters,
        on_delete=models.CASCADE,
        verbose_name='Рассылка',
        related_name='emails'
    )
    email = models.EmailField('Email', max_length=1024, db_index=True)


    class Meta:
        verbose_name = 'Email'
        verbose_name_plural = 'Emails'

    def __str__(self):
        return self.email



class OutgoingMail(models.Model):
    email = models.CharField('Email получателя', max_length=1024, db_index=True)
    subject = models.CharField('Тема', max_length=150, blank=True)
    html_content = models.TextField('Содержание письма')
    sent_date = models.DateTimeField(
        'Дата отправки', db_index=True, blank=True, null=True
    )

    class Meta:
        verbose_name = 'Исходящее письмо'
        verbose_name_plural = 'Исходящие письма'

    def __str__(self):
        return self.email


class NotificationType(models.Model):
    BY_DEFAULT    = 'by_default'

    event = models.CharField(
        'Событие',
        max_length=50,
        db_index=True,
        choices=(
            (BY_DEFAULT   , 'По умолчанию'),
    ))
    subject = models.CharField('Тема письма', max_length=100, blank=True)
    template = models.ForeignKey(
        NotifyTemplate,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Шаблон письма',
        related_name='notification_templates'
    )
    notification = models.TextField('Содержание письма', blank=True)

    class Meta:
        verbose_name = 'Тип уведомления'
        verbose_name_plural = 'Типы уведомлений'
    
    def __str__(self):
        return f'{self.subject if self.subject else self.get_event_display()}'


class Notification(models.Model):
    NOTIFICATION_TO_CLIENTS       = 'clients'
    NOTIFICATION_TO_USERS         = 'users'
    NOTIFICATION_CLIENTS_USERS    = 'both'

    email = models.EmailField('email', blank=True, db_index=True)
    use_up = models.BooleanField('использовать', default=True, db_index=True)
    notification_type = models.ForeignKey(
        NotificationType,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='тип уведомления',
        related_name='notifications'
    )
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Пользователь',
        related_name='notified_users'
    )
    notify = models.CharField(
        'Уведомлять', max_length=20, default='both', choices=(
            (NOTIFICATION_TO_CLIENTS      , 'Клиентов'),
            (NOTIFICATION_TO_USERS        , 'Пользователей'),
            (NOTIFICATION_CLIENTS_USERS   , 'Клиентов и пользователей'),
    ))

    class Meta:
        verbose_name = 'Настройка уведомления'
        verbose_name_plural = 'Найстройка уведомлений'
    
    def __str__(self):
        return self.email

