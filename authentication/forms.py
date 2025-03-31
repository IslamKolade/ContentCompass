from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import User



class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser')

    def clean_password(self):
        return self.initial["password"]
