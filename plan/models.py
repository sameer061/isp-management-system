from django.core.files.storage import default_storage
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
import uuid
# Create your models here.
from django.db import models

class Payment(models.Model): 
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_id = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=100)  # Changed to EmailField
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.payment_id}"

    class Meta:
        db_table = 'plan_payment'  
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'

class Plan(models.Model):
    DURATION = (
        ('ONE MONTH','ONE MONTH'),
        ('SIX MONTH','SIX MONTH'),
        ('TWELVE MONTH','TWELVE MONTH'),
        ('CUSTOM','CUSTOM')
    )
    plan_name = models.CharField(max_length=200,blank=False)
    description = models.TextField(max_length=500,null=True,blank=True,help_text="enter details")
    Duration = models.TextField(choices=DURATION,default='')
    cost = models.PositiveIntegerField(blank=False)
    def __str__(self):
        return str(self.plan_name)


class Userprofile(models.Model):
    user = models.CharField(max_length=200,unique=True)
    first_name = models.CharField(max_length=20, default='')
    last_name = models.CharField(max_length=20, default='')
    email=models.EmailField(max_length=200,blank=True,null=True)
    address = models.TextField(max_length=500, default='')
    profile_image=models.ImageField(blank=True,null=True, default='images/demo.jpg', upload_to='profiles')
    phoneno = PhoneNumberField(null=False, blank=False, unique=True , default='+91')
    id_proof = models.FileField(upload_to='id_proof', blank=True, null=True, )
    current_plan = models.ForeignKey(Plan, on_delete=models.CASCADE, default='')
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    is_active = models.BooleanField(default=True)




