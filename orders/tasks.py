import json
import base64
import requests
from contextlib import suppress
from django_rq import get_queue
from functools import wraps
from rq import Retry, get_current_job
from redis.exceptions import ConnectionError
from django.shortcuts import get_object_or_404

from enterprise.models import IntegrationSettings, Contacts
from mailings.tasks import create_outgoing_mail
from orders.models import Order, OrderItem, DeliveryAddresses
from prices.lib import get_delivery_price

queue = get_queue('default')

class ErrorUpdateOfStoks(BaseException):

    def __init__(self, error):
        self.error = error

    def __str__(self):
        return f'Ошибка обновления остатков: {self.error}'


def planed_update_of_stoks():
    def wrap(func):
        @wraps(func)
        def run_func(request):
            response = func(request)
            order_id = json.loads(response.content.decode()).get('InvId')
            if order_id:
                with suppress(ConnectionError):
                    queue.enqueue(
                        launch_update_of_stoks,
                        args=[order_id],
                        retry=Retry(max=10, interval=[1, 3, 5, 10, 30, 60, 60*5, 60*10, 60*30, 60*60]),
                    )
            return response
        return run_func
    return wrap


def launch_update_of_stoks(order_id):
    integration_settings = IntegrationSettings.objects.all()
    for integration_setting in integration_settings:
        if not integration_setting.link: continue
        url = integration_setting.link.replace('{order_id}', str(order_id))
        headers = {}
        if integration_setting.login:
            auth = base64.b64encode(f'{integration_setting.login}:{integration_setting.password}'.encode('utf-8')).decode("utf-8")
            headers = {"Authorization": f"Basic {auth}"}
        try:
            print(f'Authorization: {integration_setting.login}:{integration_setting.password} - {headers}')
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            if response.text !='Success':
                raise ErrorUpdateOfStoks(response.text)
        except Exception as error:
            print(f"Ошибка выполнения запроса {url}: {error} ({response.text})")
            raise error  # повтор будет автоматически инициирован


def send_by_email():
    def wrap(func):
        @wraps(func)
        def run_func(request):
            response = func(request)
            if response.status_code == 200:
                order_id = json.loads(response.content.decode()).get('InvId')
                if order_id:
                    launch_send_by_email(request, order_id)
            return response
        return run_func
    return wrap


def launch_send_by_email(request, order_id):
    context = {
        'ready_for_payment': False,
        'order': get_object_or_404(Order, pk=order_id),
        'basket': OrderItem.objects.filter(order__pk=order_id),
        'delivery_addresses': DeliveryAddresses.objects.filter(customer=request.user).order_by('-created_at'),
        'delivery_price': get_delivery_price(request),
        'read_only': True,
    }
    recipient_list = [request.user.email]
    contacts = Contacts.objects.first()
    if contacts and contacts.email: 
        recipient_list.append(contacts.email)
    if contacts and contacts.additional_email: 
        recipient_list.append(contacts.additional_email)
    create_outgoing_mail({
        'recipient_list'   : recipient_list,
        'subject'          : f'Заказ №{order_id}',
        'template'         : 'order.html',
        'content'          : '',
        'context'          : context,
        'order_id'         : order_id,
    })
