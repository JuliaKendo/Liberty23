from contextlib import suppress
from django import forms
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from orders.models import Order, OrderItem, DeliveryAddresses


class DeliveryAddressesForm(forms.ModelForm):
    class Meta:
        model = DeliveryAddresses
        fields = [
            'fname',
            'lname',
            'company',
            'address',
            'town',
            'state',
            'zip',
            'email',
            'phone', 
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fname'].required = True
        self.fields['email'].required = True


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer', 'status', 'delivery_address', 'additional_info', 'department', ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'unit', 'quantity', 'price', 'sum',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class OrderItemInlineForm(BaseInlineFormSet):

    def add_fields(self, form, index):
        super().add_fields(form, index)

    def clean(self):
        super().clean()


OrderItemInline = inlineformset_factory(
    Order,
    OrderItem,
    form = OrderItemForm,
    formset=OrderItemInlineForm,
    fields = ['product', 'unit', 'quantity', 'price', 'sum',],
    extra=0,
    can_delete=True
)
