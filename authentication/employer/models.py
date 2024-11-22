from tkinter import CASCADE
from django.db import models
from django.contrib.auth import get_user_model
import datetime
# local import
from account.models import User
# Create your models here.

# extra information about the employer
class Employer(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE , related_name="employer")
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=250)
    city = models.CharField(max_length=100)
    id_number = models.CharField(max_length=25)
    postal_code = models.CharField(max_length=25)
    
    
# opportunity that employer makes
class JobOpportunity(models.Model):
        
    class OfferStatus(models.TextChoices) :
        REGISTRED = "registered" , "Registered"
        CONFIRMED = "approved" , "Approved"
        CANCELED = "canceled" , "Canceled"
        EXPIRED = "expired" , "Expired"
        
    employer = models.ForeignKey("employer.Employer" , on_delete=models.CASCADE , related_name="job_opportunities")
    active = models.BooleanField(default=False)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    status = models.CharField(choices=OfferStatus , default=OfferStatus.REGISTRED)
    created_at = models.DateTimeField(auto_now_add=True)
    # i changed the data type of this column manually in the DB
    expire_at = models.DateField()

# basket package
class EmployerCart(models.Model) :
    employer =  models.ForeignKey(Employer , on_delete=models.CASCADE ,  related_name="carts")
    total_price = models.DecimalField(max_digits=10 , decimal_places=3 , default=0)
    active = models.BooleanField(default=True)
    is_paid = models.BooleanField(default=False)
    
# basket items
class EmployerCartItems(models.Model) : 
    cart = models.ForeignKey(EmployerCart  , on_delete=models.CASCADE , related_name="basket_items")
    package = models.ForeignKey("package.Package" , on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10 , decimal_places=3)
    quantity = models.IntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)


class ViewedResume (models.Model) :
    resume = models.ForeignKey("job_seeker.Resume" , on_delete=models.CASCADE) 
    employer = models.ForeignKey("employer.Employer" , on_delete=models.CASCADE)
    



    