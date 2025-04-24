from django import forms

from .models import Department, Appeal

        
class DepartmentsForm(forms.ModelForm):
    departments = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        widget=forms.RadioSelect,
        label=""
    )

    class Meta:
        model = Department
        fields = ('departments',)


class AppealForm(forms.ModelForm):
    title = forms.CharField(max_length=200, required = False, widget=forms.HiddenInput())
    name = forms.CharField(
        max_length=200,
        required = True,
        error_messages={
            'required': 'Имя обязательно для заполнения',
            'max_length': 'Имя не должно превышать 200 символов'
    })
    phone = forms.CharField(
        max_length=20,
        required = True,
        error_messages={
            'required': 'Телефон обязателен для заполнения',
            'max_length': 'Телефон не должен превышать 20 символов'
    })
    email = forms.EmailField(required = False, widget=forms.HiddenInput())
    content = forms.CharField(
        widget=forms.Textarea,
        required = True,
        error_messages={
            'required': 'Содержание обращения обязательно для заполнения'
        },
    )
    status = forms.ChoiceField(
        choices=(
            ('new', 'Новое'),
            ('reviewed', 'Рассмотренно'),
        ),
        initial='new',
        widget=forms.HiddenInput()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['name'].widget.attrs.update({'placeholder': 'Имя'})
        self.fields['phone'].widget.attrs.update({'placeholder': 'Телефон'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Email'})
        self.fields['content'].widget.attrs.update({'placeholder': 'Содержание обращения'})

    class Meta:
        model = Appeal
        fields = '__all__'