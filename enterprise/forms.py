from django import forms

from .models import Department


class DepartmentsForm(forms.Form):

    OPTIONS = ((item.id, item.name) for item in Department.objects.all())

    # departments = forms.MultipleChoiceField(
    #     widget=forms.CheckboxSelectMultiple,
    #     choices=OPTIONS
    # )

    departments = forms.ChoiceField(
        choices=OPTIONS,
        widget=forms.RadioSelect,
        label=""
    )

    class Meta:
        model = Department
        fields = ('departments',)

    # def __init__(self, *args, **kwargs):
    #     super(DepartmentsForm, self).__init__(*args, **kwargs)
    #     self.fields['departments'].label = ""
