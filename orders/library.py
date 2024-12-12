from functools import wraps
from django.shortcuts import get_object_or_404
from .models import Order

def check_order_status():
    def wrap(func):
        @wraps(func)
        def run_func(request, *args, **kwargs):
            params = request.POST.dict()
            order = get_object_or_404(Order, pk=params.get('InvId'))
            kwargs = kwargs | {'status': 1}
            if order.status == 'introductory':
                kwargs = kwargs | {'status': 0}
            return func(request, *args, **kwargs)
        return run_func
    return wrap
