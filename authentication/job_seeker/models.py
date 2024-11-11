from django.db import models
# local import
from account.models import User


# Create your models here.
class JobSeeker(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resume = models.FileField(upload_to='resumes/')
    # json field for the resume creation
    # resumse = models.JSONField(default=dict)

