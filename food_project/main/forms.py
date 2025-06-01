from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User  # твоя кастомная модель

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User  # Указываем свою модель
        fields = ('username', 'password1', 'password2')
