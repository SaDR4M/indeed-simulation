from django.db import models
     # local import
from account.models import User
from package.models import Package
    # Create your models here.

# extra information about the employer
class Employer(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100)
    package = models.ManyToManyField(Package , related_name='packages')
    
# opportunity that employer makes
class JobOpportunity(models.Model):

    employer = models.ForeignKey(Employer , on_delete=models.CASCADE , related_name="employers")
    active = models.BooleanField(default=True)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    expire_at = models.DateTimeField()


    
