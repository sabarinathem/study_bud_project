from dataclasses import field
from  django import forms
from .models import Room
from .models import User
from django.contrib.auth.forms import UserCreationForm



class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = "__all__"
        exclude = ['host','participants'] # remove two fields from the roomform

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['avathar','name','username','email','bio']


class UserRegisterForm(UserCreationForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """
    error_messages = {
        'password_mismatch': ("The two password fields didn't match."),
    }

    name = forms.CharField(
        label="Full Name",
        widget=forms.TextInput(attrs={'placeholder':'eg.John Smith'})
    )

    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={'placeholder':'eg.john'}))
    
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'placeholder':'eg.john@gmail.com'})
    )

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'placeholder':'Password'}))
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput(attrs={'placeholder':'Confirm Password'}))
    
    class Meta:
        model = User
        fields = ['name','username','email','password1','password2']