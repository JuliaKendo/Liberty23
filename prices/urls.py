from django.urls import path

from . import views

app_name = "prices"

urlpatterns = [
    path('upload', views.upload_price),
    path('upload/delivery', views.upload_delivery_price),        
]
