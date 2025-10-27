import datetime

from functools import wraps
from contextlib import suppress

from django.conf import settings
from django.core.mail import EmailMessage

from django.template import Template, Context
from django.template.loader import render_to_string

from django.core.exceptions import ValidationError

from django_rq import job, get_queue
from redis.exceptions import ResponseError

from .models import (
    OutgoingMail,
    MailingOfLetters,
    NotificationType,
    Notification,
    Emails,
)


MAX_NUM_OF_EMAIL_ADDRESSES_SENT = 1
DEFAULT_TIMEOUT_FOR_SENDING_EMAILS = 1

# SEND EMAIL:

def launch_mailing():
    def wrap(func):
        @wraps(func)
        def run_func(*args):
            mail_params, = args
            if not mail_params:
                return OutgoingMail.objects.none
            unset_mail = func(mail_params)
            mail_params = {key: value for key, value in mail_params.items() if key != 'recipient_list'} | {
                'subject': unset_mail.subject,
                'obj_id': unset_mail.id
            }
            email_addresses = unset_mail.email.split(';')
            grouped_email_addresses = [
                email_addresses[i:i + MAX_NUM_OF_EMAIL_ADDRESSES_SENT]\
                    for i in range(
                        0, len(email_addresses), MAX_NUM_OF_EMAIL_ADDRESSES_SENT
            )]
            for i, emails in enumerate(grouped_email_addresses):
                current_queue = get_queue()
                current_queue.enqueue_in(
                    datetime.timedelta(minutes=DEFAULT_TIMEOUT_FOR_SENDING_EMAILS+i),
                    send_email, unset_mail.html_content, emails, **mail_params
                )
            return unset_mail

        return run_func
    return wrap


@job('default')
def send_email(html_content, recipient_list, **params):
    for recipient in recipient_list:
        email = EmailMessage(
            params['subject'],
            html_content,
            f'Интернет магазин <{settings.EMAIL_HOST_USER}>',
            [recipient],
            # reply_to=['TALANT<opt@talantgold.ru>'],
        )
        email.content_subtype = "html"
        email.send()

    if params.get('obj_id'):
        OutgoingMail.objects.filter(id=params['obj_id']).update(
            sent_date=datetime.datetime.now()
        )

    if params.get('mailing_of_letter'):
        mailing_of_letter = params.get('mailing_of_letter')
        mailing_of_letter.status = MailingOfLetters.COMPLETED
        mailing_of_letter.save(update_fields=['status'])


# PREPARE EMAIL:

def get_email_addresses(emails):
    email_addresses = emails.values_list('email', flat=True)
    
    if email_addresses:
        return [email_addresse for email_addresse in email_addresses]


def get_recipient_list(notification_type, email):
    result = []
    notifications = Notification.objects.filter(use_up=True, notification_type=notification_type)
    for notify in notifications:
        if notify.email:
            result = result + [notify.email]
        if  notify.notify in [
                Notification.NOTIFICATION_TO_USERS,
                Notification.NOTIFICATION_CLIENTS_USERS
            ] and notify.user and notify.user.email:
            result = result + [notify.user.email]
    if notifications.exclude(notify=Notification.NOTIFICATION_TO_CLIENTS):
        result = result + [email]
    return list(set(result))


def get_context(notification_type, **kwargs):
    '''
        Return dict of context for email template.

        notification_type - (str) type of notification
        email - (str) email address
        kwargs - (dict) additional params
    '''
    result = {}

    if notification_type == NotificationType.BY_DEFAULT:
        pass

    return result


def get_mail_params(notification_options):
    '''
        Return dict of mail parametrs.

        notification_options - dict with next keys:
            notification_type - (str) type of notification
            id - (str) object id
            url - (str) url
            params - (str) json dumps of object
    '''
    notification_types = NotificationType.objects.filter(event=notification_options['notification_type'])
    for obj in notification_types:
        subject  = obj.subject
        letter_content = obj.notification
        letter_template = obj.template
        with suppress(
            NotificationType.DoesNotExist,
            ValidationError,
            ValueError,
            AttributeError,
            ResponseError
        ):
            if not letter_content:
                raise ValidationError('Не указано содержание письма', code='')
            email, context = get_context(**notification_options)
            recipient_list = get_recipient_list(obj, email)
            return {
                'context': context,
                'recipient_list': recipient_list,
                'subject': subject,
                'template': letter_template,
                'content':letter_content
            }


@launch_mailing()
def create_outgoing_mail(mail_params):
    if mail_params['content']:
        letter_content = mail_params['content']
        template = Template(letter_content)
        rendered_html = template.render(Context(mail_params['context']))
        html_content = render_to_string('forms/notify-template.html', {'params': rendered_html})
    else:
        html_content = render_to_string(mail_params['template'], mail_params['context'])
    return OutgoingMail.objects.create(
        email=';'.join(mail_params['recipient_list']),
        subject=mail_params['subject'],
        html_content=html_content
    )

