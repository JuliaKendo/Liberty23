from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .forms import SignUpForm
from enterprise.forms import AppealForm


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Вы успешно зарегистрировались!')
            return JsonResponse({'is_authenticated': request.user.is_authenticated})
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


def profile(request):
    return JsonResponse({'is_authenticated': request.user.is_authenticated})


def user_logout(request):
    logout(request)
    return redirect("start_page")


@api_view(['GET'])
def is_user_authenticated(request):
    return JsonResponse({'is_authenticated': request.user.is_authenticated})


class AuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })


def contact(request):
    appeal_form = AppealForm()
    return render(request, 'contact.html', context={'form': appeal_form})