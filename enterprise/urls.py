from django.urls import path
from django.shortcuts import render

from . import views

app_name = "enterprise"

urlpatterns = [
    path('news', views.NewsView.as_view(), name='news'),
    path('appeals/add', views.appeal_add, name='appeal'),
    path('upload/departments', views.upload_departments),
    path('departments', views.departments, name='departments'),
    path('payments/params', views.get_payment_params),
    path('payments/check', views.check_payment),
    path('info', views.InfoView.as_view(), name='info'),
]
