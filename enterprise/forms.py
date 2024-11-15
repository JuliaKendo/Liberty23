from django import forms

from .models import Department

        
class DepartmentsForm(forms.ModelForm):
    departments = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        widget=forms.RadioSelect,
        label=""
    )

    class Meta:
        model = Department
        fields = ('departments',)
