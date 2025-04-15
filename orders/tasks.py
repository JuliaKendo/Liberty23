import json
import requests
from contextlib import suppress
from django_rq import get_queue
from functools import wraps
from rq import Retry, get_current_job
from redis.exceptions import ConnectionError

from enterprise.models import IntegrationSettings

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
                        retry=Retry(max=5, interval=[60, 60*5, 60*10, 60*30, 60*60]),
                    )
            return response
        return run_func
    return wrap


def launch_update_of_stoks(order_id):
    integration_settings = IntegrationSettings.objects.all()
    for integration_setting in integration_settings:
        if not integration_setting.link: continue
        url = integration_setting.link.replace('{order_id}', str(order_id))
        try:
            response = requests.get(url)
            response.raise_for_status()
            if response.text !='Success':
                raise ErrorUpdateOfStoks(response.text)
        except Exception as error:
            print(f"Ошибка выполнения запроса {url}: {error} ({response.text})")
            raise error  # повтор будет автоматически инициирован
