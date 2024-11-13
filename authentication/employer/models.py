from django.db import models
from django.contrib.auth import get_user_model
import datetime
# local import
from account.models import User

# from package.models import Package
Package = get_user_model()
    
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

    employer = models.ForeignKey(Employer , on_delete=models.CASCADE , related_name="job_opportunities")
    active = models.BooleanField(default=True)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_created=True )
    # changed the type of this column manually in the DB
    expire_at = models.DateField()




    
