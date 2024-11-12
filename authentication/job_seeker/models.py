from django.db import models
from django.contrib.auth import get_user_model
# local import
from account.models import User
#from authentication.employer.models import JobOpportunity
JobOpportunity = get_user_model()
# Create your models here.

# specifc information about the job seeker
class JobSeeker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True , null=True)
    created_at = models.DateTimeField(auto_created=True)


# resume of the job seeker
class Resume(models.Model) :
    job_seeker = models.ForeignKey(JobSeeker , on_delete=models.CASCADE)
    file = models.FileField(upload_to='resumes/')
    created_at = models.DateTimeField(auto_created=True)
    updated_at = models.DateTimeField(auto_now=True)
    skills = models.JSONField(default=dict, blank=True , null=True)
    exprience = models.TextField(blank=True , null=True)
    education = models.TextField(blank=True , null=True)
    
# job seeker apply for job
class Application(models.Model) :
    class ApplicationStatus(models.IntegerChoices):
        SENT = 0 , 'sent'
        REJECTED = 1 , 'rejected'
        SEEN = 2 , 'seen'
        INTERVIEW = 3 , 'interview'
        ACCEPTED = 4 , 'accepted'

    job_seeker = models.ForeignKey(JobSeeker, on_delete=models.CASCADE)
    job_opportunity = models.ForeignKey(JobOpportunity , on_delete=models.CASCADE)
    send_at = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=ApplicationStatus.choices, default=ApplicationStatus.SENT)
    description = models.TextField()
    
 

    