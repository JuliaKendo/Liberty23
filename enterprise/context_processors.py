from .models import Contacts, Manager
from .departments import СurrentDepartment


def contact(request):
    return {'contact': Contacts.objects.first()}


def managers_phone(request):
    phones = [item[0] for item in Manager.objects.values_list('phone') if item]
    contact = Contacts.objects.first()
    phones.append(contact.phone) 
    return {'phones': set(phones)}


def department(request):
    current_department = СurrentDepartment(request)
    return {'department': current_department.department}
