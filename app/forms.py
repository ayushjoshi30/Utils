# app/forms.py

from django import forms
from .models import AppUser
from django.contrib.auth.forms import AuthenticationForm


class AppUserForm(forms.ModelForm):
    class Meta:
        model = AppUser
        fields = ['first_name', 'last_name', 'user_name', 'email', 'mobile_no', 'password', 'is_active', 'is_admin']

    # Adding custom styling to indicate required fields
    def __init__(self, *args, **kwargs):
        super(AppUserForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            if field.required:
                field.widget.attrs['class'] = 'required-field'
class LoginForm(forms.Form):
    username = forms.CharField(max_length=255)
    password = forms.CharField(widget=forms.PasswordInput())
    
class FileUploadForm(forms.Form):
    file = forms.FileField(label="Choose a file to upload")