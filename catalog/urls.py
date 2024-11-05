from django.urls import path
from django.shortcuts import render

from . import views

app_name = "catalog"

urlpatterns = [
    path('products', views.ProductsView.as_view(), name='products'),
    path('product/<slug:id>/', views.ProductCardView.as_view(), name='product'),
    # path('product', render, kwargs={'template_name': 'product-details.html'}, name='product'),
    path('upload/categories', views.upload_categories),
    path('upload/products', views.upload_products),
    path('upload/images', views.upload_images),
]
