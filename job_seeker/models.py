from django.db import models
from django.contrib.auth import get_user_model
# local import
from account.models import User
from location.models import Cities , Provinces
from core.mixins import GenderMixin
from core.choices import ExperienceChoices , EducationChoices 
from manager.models import TechnologyCategory
# Create your models here.



# mixin model for active , created at and delted at
class TestStatusMixin(models.Model) :
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True , blank=True)

    class Meta :
        abstract = True

    

# specific information about the job seeker
class JobSeeker(GenderMixin):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE , related_name='job_seeker')
    bio = models.TextField(blank=True , null=True , help_text="a brief text about the job seeker")
    created_at = models.DateTimeField(auto_now_add=True)
    province = models.ForeignKey(Provinces , related_name="state_jobseekers" , on_delete=models.CASCADE , default=8)
    city = models.ForeignKey(Cities , related_name="city_jobseekers" , on_delete=models.CASCADE , default=301)
    is_banned = models.BooleanField(default=False)
    banned_by = models.ForeignKey(User, related_name="banned_jobseekers", on_delete=models.CASCADE, null=True, blank=True)   
    banned_at = models.DateTimeField(null=True , blank=True)
    banned_description = models.CharField(max_length=255 , null=True , blank=True)





class Test(TestStatusMixin) :
    
    class TestKind(models.TextChoices) :
        PSYCHOLOGY = "psychology"
        QUESTIONNAIRE = "questionnaire" 

    
    user = models.ForeignKey(User , on_delete=models.CASCADE , related_name="tests")
    title = models.CharField(max_length=50 , null=False ,blank=False)
    kind = models.CharField(choices=TestKind.choices)
    publish = models.BooleanField(default=False)
    count = models.IntegerField(default=10)
 
    
class Question(TestStatusMixin) :
    test = models.ForeignKey(Test , on_delete=models.CASCADE , related_name="questions")
    user = models.ForeignKey(User , on_delete=models.CASCADE , related_name="questions")
    question = models.TextField(null=False)
    score = models.TextField(null=False , default=5)        
    
class Answer(models.Model) :
    user = models.ForeignKey(User , on_delete=models.CASCADE , related_name="answers")
    question = models.ForeignKey(Question , on_delete=models.CASCADE , related_name="answers")
    answer = models.TextField(null=False , blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    

# TODO add state to it
# resume of the job seeker
class Resume(models.Model) :    
    job_seeker = models.OneToOneField(JobSeeker , on_delete=models.CASCADE )
    file = models.FileField(upload_to='resumes/' , null=True , blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    skills = models.JSONField(default=dict , null=True)
    experience = models.CharField(choices=ExperienceChoices)
    education = models.CharField(choices=EducationChoices)
    # TODO remove null and blank
    stack = models.ManyToManyField(TechnologyCategory , related_name="resume" , null=True , blank=True)
    
    test = models.ManyToManyField(Test , related_name="resume")
    
    
    
    
# job seeker apply for job
class Application(models.Model) :
    
    class ApplicationStatus(models.TextChoices):
        SENT = "sent" , 'Sent'
        REJECTED = "rejected" , 'Rejected'
        SEEN = 'seen' , 'Seen'
        INTERVIEW = 'interview' , 'Interview'
        ACCEPTED = 'accepted' , 'Accepted'

    job_seeker = models.ForeignKey(JobSeeker, on_delete=models.CASCADE , related_name='seeker_applications')
    job_opportunity = models.ForeignKey("employer.JobOpportunity" , on_delete=models.CASCADE , related_name='offer_applications')
    send_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=ApplicationStatus , default=ApplicationStatus.SENT)
    description = models.TextField(null=True , blank=True)
    