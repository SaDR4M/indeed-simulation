from django.db import models
from django.contrib.auth import get_user_model
# local import
from account.models import User
#from authentication.employer.models import JobOpportunity
# JobOpportunity = get_user_model()
from employer.models import JobOpportunity
# Create your models here.

# specific information about the job seeker
class JobSeeker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE , related_name='job_seeker')
    bio = models.TextField(blank=True , null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    birthday = models.DateField()


# resume of the job seeker
class Resume(models.Model) :
    job_seeker = models.ForeignKey(JobSeeker , on_delete=models.CASCADE , related_name='resumes')
    file = models.FileField(upload_to='resumes/' , null=True , blank=True )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    skills = models.JSONField(default=dict)
    experience = models.TextField(max_length=200)
    education = models.TextField(max_length=200)


    
# job seeker apply for job
class Application(models.Model) :
    class ApplicationStatus(models.IntegerChoices):
        SENT = 0 , 'sent'
        REJECTED = 1 , 'rejected'
        SEEN = 2 , 'seen'
        INTERVIEW = 3 , 'interview'
        ACCEPTED = 4 , 'accepted'

    job_seeker = models.ForeignKey(JobSeeker, on_delete=models.CASCADE , related_name='seeker_applications')
    job_opportunity = models.ForeignKey(JobOpportunity , on_delete=models.CASCADE , related_name='offer_applications')
    send_at = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=ApplicationStatus.choices, default=ApplicationStatus.SENT)
    description = models.TextField(null=True , blank=True)
    
 

    