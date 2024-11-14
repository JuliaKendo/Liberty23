from django.urls import path
from django.shortcuts import render

from . import views

app_name = "enterprise"

urlpatterns = [
    path('news', views.NewsView.as_view(), name='news'),
    path('upload/departments', views.upload_departments),
    path('departments', views.departments, name='departments'),
]
