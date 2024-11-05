from .models import Contacts

def contact(request):
    return {'contact': Contacts.objects.first()}
