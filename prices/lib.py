from enterprise.departments import СurrentDepartment
from .models import DeliveryPrice


def get_delivery_price(request):
    current_department = СurrentDepartment(request)
    if current_department and current_department.department:
        delivery_prices = DeliveryPrice.objects.available_delivery_price(current_department.department)
        if delivery_prices:
            delivery_price = delivery_prices.first()
            return delivery_price.actual_price
    
    return 0 
