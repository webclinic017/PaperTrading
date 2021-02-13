from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class CreateUserForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'password1', 'password2', 'broker', 'api_key', 'secret_key']
