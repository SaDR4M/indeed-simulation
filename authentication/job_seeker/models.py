from django.db import models
# local import
from account.models import User

from authentication.employer.models import Employer


# Create your models here.
class JobSeeker(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resume = models.FileField(upload_to='resumes/')

    # json field for the resume creation
    # resumse = models.JSONField(default=dict)

class ResumeView(models.Model) :
    class ResumeStatus(models.IntegerChoices):
        SENT = 0 , 'sent'
        REJECTED = 1 , 'rejected'
        SEEN = 2 , 'seen'
        INTERVIEW = 3 , 'interview'
        ACCEPTED = 4 , 'accepted'

    job_seeker = models.ForeignKey(JobSeeker, on_delete=models.CASCADE)
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)
    view_at = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=ResumeStatus.choices, default=ResumeStatus.SENT)
    description = models.TextField()