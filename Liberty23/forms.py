from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    agree_to_terms = forms.BooleanField(
        label="Принимаю условия предоставления услуг",
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'checked': False, 'style': 'display: none;',}),
        error_messages={'required': 'Вы должны согласиться с условиями предоставления услуг.'}
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'agree_to_terms')

        help_texts = {field: '' for field in fields}
