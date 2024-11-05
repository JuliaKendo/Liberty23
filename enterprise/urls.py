from django.urls import path
from django.shortcuts import render

from . import views

app_name = "enterprise"

urlpatterns = [
    path('news', views.NewsView.as_view(), name='news'),
]
