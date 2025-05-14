from django import forms
from .models import Plan,Userprofile,Payment
from django.contrib.auth.models  import  User


class planform(forms.ModelForm):
    class Meta:
        model = Plan
        fields = '__all__'

class  clientform(forms.ModelForm):
    class Meta:
        model = Userprofile
        fields ='__all__'

class Payment(forms.ModelForm):
    class Meta:
        model = Payment
        fields = '__all__'