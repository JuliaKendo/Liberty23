from django.urls import path, re_path, register_converter
from django.shortcuts import render
from datetime import datetime

from . import views

class DateConverter:
    regex = '\d{4}-\d{2}-\d{2}'

    def to_python(self, value):
        return datetime.strptime(value, '%Y-%m-%d')

    def to_url(self, value):
        return value    

register_converter(DateConverter, 'data')

app_name = "orders"

urlpatterns = [
    # path('checkout', render, kwargs={'template_name': 'checkout.html'}, name='checkout'),
    # re_path(r'^$', views.orders, name='all'),
    
    path('', views.OrdersView.as_view(), name='list'),
    path('checkout', views.CheckoutView.as_view(), name='checkout'),
    path('pre-order', views.PreOrderView.as_view(), name='pre-order'),
    re_path(r'^order/(?P<order_id>\d+)/$', views.OrderView.as_view(), name='order'),
    re_path(r'^add/$', views.order_add, name='add'),
    re_path(r'^remove/$', views.order_remove, name='remove'),
    re_path(r'^remove/(?P<order_id>\d+)/$', views.order_remove, name='remove'),
    # re_path(r'^/check/$', views.order_add, name='add'),

    path('export', views.unload_orders),
    path('export/<order_id>', views.unload_orders),
    path('export/<data:data_from>', views.unload_orders),
    path('export/<data:data_from>/<data:data_to>', views.unload_orders),

    path('payment/result', views.handle_result_payment),
]
