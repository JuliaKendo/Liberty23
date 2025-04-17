from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer, ListSerializer

from .models import Price, PriceType, DeliveryPrice 
from catalog.models import Product
from enterprise.models import Department
from catalog.views import CategorySerializer
from catalog.views import get_or_update_product


def get_or_update_price_type(data):
    price_type_data = dict(data.pop('type'))
    price_type, _ = PriceType.objects.update_or_create(
        name=price_type_data.get('name', '')
    )
    return price_type

class DepartmentSerializer(ModelSerializer):
    
    class Meta:
        model = Department
        fields = '__all__'

    def create(self, validated_data):
        department, _ = Department.objects.get_or_create(
            identifier_1C=validated_data['identifier_1C'],
            defaults=validated_data
        )
        return department

class PriceTypeSerializer(ModelSerializer):

    class Meta:
        model = PriceType
        fields = '__all__'


class ProductSerializer(ModelSerializer):

    category = CategorySerializer()
    departments = DepartmentSerializer(many=True)

    class Meta:
        model = Product
        fields = '__all__'


class PriceListSerializer(ListSerializer):

    def update(self, _, validated_data):
        ret = []
        for item in validated_data:
            price_entry, _ = Price.objects.update_or_create(
                start_at = item.pop('start_at', timezone.now()),
                type = get_or_update_price_type(item),
                product = get_or_update_product(item),
                defaults = item
            )
            ret.append(price_entry)

        return ret


class PriceSerializer(ModelSerializer):

    type = PriceTypeSerializer()
    product = ProductSerializer()

    class Meta:
        model = Price
        fields = '__all__'
        list_serializer_class = PriceListSerializer


class DeliveryPriceListSerializer(ListSerializer):

    def update(self, _, validated_data):
        ret = []
        for item in validated_data:
            serializer = DepartmentSerializer(data=item.pop('department'))
            if serializer.is_valid():
                department = serializer.save()
                price_entry, _ = DeliveryPrice.objects.update_or_create(
                    start_at = item.pop('start_at', timezone.now()),
                    department = department,
                    defaults = item
                )
                ret.append(price_entry)

        return ret


class DeliveryPriceSerializer(ModelSerializer):
    
    department = DepartmentSerializer()

    class Meta:
        model = DeliveryPrice
        fields = '__all__'
        list_serializer_class = DeliveryPriceListSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_price(request):
    serializer = PriceSerializer(instance='', data=request.data, many=True)
    if serializer.is_valid():
        serializer.save()
        return Response('success upload', status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_delivery_price(request):
    serializer = DeliveryPriceSerializer(instance='', data=request.data, many=True)
    if serializer.is_valid():
        serializer.save()
        return Response('success upload', status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
