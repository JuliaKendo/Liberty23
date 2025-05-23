"""Liberty23 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('', render, kwargs={'template_name': 'index.html'}, name='start_page'),
    path('about', render, kwargs={'template_name': 'about.html'}, name='about_page'),
    path('contact', views.contact, name='contact_page'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', views.signup, name='signup'),
    path('accounts/profile/', views.profile, name='profile'),
    path('logout', views.user_logout, name='logout'),
    path('catalog/', include('catalog.urls')),
    path('prices/', include('prices.urls')),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('enterprise/', include('enterprise.urls')),
    path('terms_of_service', render, kwargs={'template_name': 'terms_of_service.html'}, name='terms_of_service'),

    path('is_user_authenticated/', views.is_user_authenticated),
    path('auth-token/', views.AuthToken.as_view()),

    path('summernote/'  , include('django_summernote.urls')),

    path('django-rq/'   , include('django_rq.urls')),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
