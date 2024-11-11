from django.db import models
# local import
from account.models import User

from authentication.employer.models import Employer , JobOpportunity

# Create your models here.
class JobSeeker(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True , Null=True)
    created_at = models.DateTimeField(auto_created=True)



class Resume(models.Model) :
    job_seeker = models.ForeignKey(JobSeeker , on_delete=models.CASCADE)
    file = models.FileField(upload_to='resumes/')
    created_at = models.DateTimeField(auto_created=True)
    updated_at = models.DateTimeField(auto_now=True)
    skills = models.JSONField(default=dict , blank=True , null=True)
    exprience = models.TextField(blank=True , null=True)
    education = models.TextField(blank=True , null=True)
    
    
class Application(models.Model) :
    class ApplicationStatus(models.IntegerChoices):
        SENT = 0 , 'sent'
        REJECTED = 1 , 'rejected'
        SEEN = 2 , 'seen'
        INTERVIEW = 3 , 'interview'
        ACCEPTED = 4 , 'accepted'

    job_seeker = models.ForeignKey(JobSeeker, on_delete=models.CASCADE)
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)
    view_at = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=ApplicationStatus.choices, default=ApplicationStatus.SENT)
    description = models.TextField()
    
 

    