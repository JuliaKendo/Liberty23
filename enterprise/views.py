import hashlib
import requests
from contextlib import suppress
from django.db import transaction
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer, ListSerializer

from requests.exceptions import HTTPError, ConnectionError
import xml.etree.ElementTree as ET

from .models import News, Department, PaymentSetup
from .forms import DepartmentsForm, AppealForm
from .departments import СurrentDepartment
from orders.library import check_order_status


class DepartmentListSerializer(ListSerializer):

    def update(self, instance, validated_data):
        ret = []
        for item in validated_data:   
            department, _ = Department.objects.get_or_create(
                identifier_1C=item.pop('identifier_1C', ''),
                defaults=item
            )
            ret.append(department)
        return ret


class DepartmentSerializer(ModelSerializer):
    
    class Meta:
        model = Department
        fields = '__all__'
        list_serializer_class = DepartmentListSerializer


class PaymentSetupSerializer(ModelSerializer):

    class Meta:
        model = PaymentSetup
        fields = '__all__'


class NewsView(ListView):
    model = News
    template_name = 'news.html'
    context_object_name = 'news'
    allow_empty = True
    paginate_by = 5
    
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.order_by('-created_at')

    def get_context_data(self, *, object_list=None, **kwargs):
        self.object_list = self.get_queryset()
        context = super().get_context_data(**kwargs)

        paginator = Paginator(context['news'], self.paginate_by)
        page = self.request.GET.get('page')
        
        try:
            news_page = paginator.page(page)
        except PageNotAnInteger:
            news_page = paginator.page(1)
        except EmptyPage:
            news_page = paginator.page(paginator.num_pages)

        context['products']  = news_page
        context['MEDIA_URL'] = settings.MEDIA_URL

        return context


@require_POST
def appeal_add(request):
    try:
        with transaction.atomic(): 
            appeal_form = AppealForm({k: v[0] for k, v in request.POST.lists()})
            if appeal_form.is_valid():  
                appeal_instance = appeal_form.save(commit=False)
                appeal_instance.save()
            else:
                raise ValidationError(appeal_form.errors)

    except ValidationError as errors:
        transaction.rollback()
        return render(request, 'contact.html', context={'form': appeal_form})

    finally:
        if transaction.get_autocommit():
            transaction.commit()

    return render(request, 'contact.html', context={'form': AppealForm()})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_departments(request):
    serializer = DepartmentSerializer(instance='', data=request.data, many=True)
    if serializer.is_valid():
        serializer.save()
        return Response('success upload', status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def departments(request):
    if request.method == 'POST':
        department = СurrentDepartment(request)
        form = DepartmentsForm(request.POST)
        if form.is_valid():
            with suppress(Department.DoesNotExist): 
                department.update(form.cleaned_data.get('departments'))
        return redirect("/catalog/products")
    else:
        form = DepartmentsForm()
    return render(request, 'forms/departments.html', {'form': form})


@api_view(['POST'])
def get_payment_params(request, *args, **kwargs):

    def calculate_signature(*args):
        """Create signature MD5.
        """
        return hashlib.md5(':'.join(str(arg) for arg in args).encode()).hexdigest()
    
    payment_params = PaymentSetupSerializer(PaymentSetup.objects.first()).data
    result = {key:value.replace(',','.') if key=='OutSum' else value for key, value in request.POST.dict().items()} | {
        'MerchantLogin': payment_params.get('merchant_login')
    }
    result = result | {
        'SignatureValue': calculate_signature(
            result['MerchantLogin'], result['OutSum'],
            result['InvId'], payment_params['password1']
        )
    }
    if payment_params.get('is_test'):
        result = result | {'IsTest': '1'}

    return JsonResponse(result, status=200, safe=False)


@api_view(['POST'])
@check_order_status()
def check_payment(request, *args, **kwargs):
    def calculate_signature(*args):
        """Create signature MD5.
        """
        return hashlib.md5(':'.join(str(arg) for arg in args).encode()).hexdigest()

    payment_status = {key: value for key, value in kwargs.items() if key == 'status'}
    params = request.POST.dict()
    payment_params = PaymentSetupSerializer(PaymentSetup.objects.first()).data

    query_params = {
        'MerchantLogin': payment_params.get('merchant_login'),
        'InvoiceID': params.get('InvId'),
        'Signature': calculate_signature(
            payment_params.get('merchant_login'),
            params.get('InvId'),
            payment_params['password2']
        )
    }
    if query_params:
        try:
            response = requests.get(
                'https://auth.robokassa.ru/Merchant/WebService/Service.asmx/OpStateExt',
                params=query_params,
            )
            response.raise_for_status()
        except (HTTPError, ConnectionError):
            pass
        except Exception:
            pass
        else:
            xml_content = response.content.decode('utf-8-sig')
            root = ET.fromstring(xml_content)
            namespaces = {'ns': 'http://merchant.roboxchange.com/WebService/'}
            result = root.find('.//ns:Result', namespaces)
            code = result.find('ns:Code', namespaces).text
            if code == '0':
                payment_status = {'status': 1}

    return JsonResponse(payment_status, status=200, safe=False)
