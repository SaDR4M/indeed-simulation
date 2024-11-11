from django.db import models
# local import
from account.models import User
from package.models import Package
# Create your models here.

class JobOpportunity(models.Model):

    active = models.BooleanField(default=True)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    expire_at = models.DateTimeField()


class Employer(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100)
    job_opportunity = models.ManyToManyField(JobOpportunity, related_name='job_opportunities')
    package = models.ManyToManyField(Package , related_name='packages')
