from django import forms
from django.contrib.auth.models import User
from .models import Item

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['title', 'description', 'location', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Black leather wallet'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe the item in detail — color, brand, markings…'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Central Park, near the fountain'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
