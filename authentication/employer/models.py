from django.db import models
# local import
from account.models import User
from payment.models import Payment
# Create your models here.
class Employee(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    
class JobOpportunity(models.Model):
    employee = models.ManyToManyField(Employee , related_name='job_opportunities')