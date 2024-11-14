from .models import Contacts
from .departments import СurrentDepartment


def contact(request):
    return {'contact': Contacts.objects.first()}


def department(request):
    current_department = СurrentDepartment(request)
    return {'department': current_department.department}
