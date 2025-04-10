from django.urls import path, re_path
from django.shortcuts import render

from . import views

app_name = "cart"

urlpatterns = [
    re_path(r'^$', views.cart_detail, name='cart_detail'),
    re_path(r'^add/(?P<product_id>\d+)/$', views.cart_add, name='add'),
    re_path(r'^sub/(?P<product_id>\d+)/$', views.cart_sub, name='sub'),
    re_path(r'^remove/(?P<product_id>\d+)/$', views.cart_remove, name='remove'),
    re_path(r'^update/(?P<product_id>\d+)/$', views.cart_update, name='update'),
    re_path(r'^mini/$', views.mini_cart_detail, name='mini_cart_detail'),
    re_path(r'^amounts/$', views.cart_amounts, name='cart_amounts'),
]
