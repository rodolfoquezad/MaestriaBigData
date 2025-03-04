from django import forms
from backend.models import *

class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'first_name', 'last_name')

        widgets = {
            'email': forms.EmailInput(attrs={'type':'email','class':'form-control form-control-lg','id':'email','placeholder':'Email'}),
            'username': forms.TextInput(attrs={'type':'text','class':'form-control form-control-lg','id':'username','placeholder':'Username'}),
            'password': forms.PasswordInput(attrs={'type':'password','class':'form-control form-control-lg','id':'password','placeholder':'Password'}),
            'first_name': forms.TextInput(attrs={'type':'text','class':'form-control form-control-lg','id':'first_name','placeholder':'First Name'}),
            'last_name': forms.TextInput(attrs={'type':'text','class':'form-control form-control-lg','id':'last_name','placeholder':'Last Name'})
        }

class LoginForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('email', 'password')

        widgets = {
            'email': forms.EmailInput(attrs={'type':'email','class':'form-control form-control-lg','id':'email','placeholder':'Email'}),
            'password': forms.PasswordInput(attrs={'type':'password','class':'form-control form-control-lg','id':'password','placeholder':'Password'})
        }

class ResetPForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('email',)

        widgets = {
            'email': forms.EmailInput(attrs={'type':'email','class':'form-control form-control-lg','id':'email','placeholder':'Email'})
        }