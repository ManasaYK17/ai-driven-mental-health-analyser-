from django import forms
from django.contrib.auth.models import User
from .models import Appointment, WellnessTask

class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class AdminLoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['counselor', 'date']

class WellnessTaskForm(forms.ModelForm):
    class Meta:
        model = WellnessTask
        fields = ['task', 'date']
