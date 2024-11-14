from contextlib import suppress
from django.conf import settings

from .models import Department


class СurrentDepartment(object):

    def __init__(self, request):
        self.session = request.session
        department_id = self.session.get(settings.DEPARTMENT_SESSION_ID)
        if not department_id:
            department_id = self.session[settings.DEPARTMENT_SESSION_ID] = 0
        self.department = None
        with suppress(Department.DoesNotExist):
            self.department = Department.objects.get(id=department_id)

    def update(self, department):
        self.department = department
        self.save()

    def save(self):
        self.session[settings.DEPARTMENT_SESSION_ID] = self.department.id
