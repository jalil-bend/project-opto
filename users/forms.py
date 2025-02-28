from django import forms
from django.contrib.auth.forms import UserChangeForm
from .models import User, Patient

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        labels = {
            'username': "Nom d'utilisateur",
            'email': 'Email',
            'first_name': 'Prénom',
            'last_name': 'Nom'
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class PatientUpdateForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['date_of_birth', 'gender']
        labels = {
            'date_of_birth': 'Date de naissance',
            'gender': 'Sexe'
        }
        widgets = {
            'date_of_birth': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                }
            ),
            'gender': forms.Select(attrs={'class': 'form-control'})
        }

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, label='Nom')
    email = forms.EmailField(label='Email')
    message = forms.CharField(widget=forms.Textarea, label='Message')

class AccessCodeForm(forms.Form):
    access_code = forms.CharField(label='Code d\'accès', max_length=8)
