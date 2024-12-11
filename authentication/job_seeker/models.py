from django.db import models
from django.contrib.auth import get_user_model
# local import
from account.models import User , Countries ,Cities , States
from common.mixins import GenderMixin
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
    bio = models.TextField(blank=True , null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    birthday = models.DateField()
    country = models.ForeignKey(Countries , related_name="city_jobseekers" , on_delete=models.CASCADE)
    state = models.ForeignKey(States , related_name="state_jobseekers" , on_delete=models.CASCADE)
    city = models.ForeignKey(Cities , related_name="city_jobseekers" , on_delete=models.CASCADE)
   





class Test(TestStatusMixin) :
    
    class TestKind(models.TextChoices) :
        PSYCHOLOGY = "psychology"
        QUESTIONNAIRE = "questionnaire" 

    
    user = models.ForeignKey(User , on_delete=models.CASCADE , related_name="tests")
    title = models.CharField(max_length=50 , null=False ,blank=False)
    kind = models.CharField(choices=TestKind.choices)
    publish = models.BooleanField(default=False)
    count = models.IntegerField(default=10)
 
    
class QuestionAndAnswers(TestStatusMixin) :
    test = models.ForeignKey(Test , on_delete=models.CASCADE , related_name="questions")
    user = models.ForeignKey(User , on_delete=models.CASCADE , related_name="question_answers")
    question = models.TextField(null=False)
    answer = models.TextField(null=True , blank=True)
    score = models.TextField(null=False , default=5)        
    

    

# TODO add state to it
# resume of the job seeker
class Resume(models.Model) :
    
    class EducationChoices(models.TextChoices) :
        UNDER_DIPLOMA = "under_diploma" 
        BACHELOR = "bachelor"
        DIPLOMA = "diploma"
        MASTER =  "master"
        PHD = "phd"
        
        
    class StackChoices(models.TextChoices) :
        FRONT_END = "front_end"  
        BACK_END = "back_end"
        FULL_STACK = "full_stack"
        WORDPRESS = "wordpress"
        GRAPHIC_DESIGNER = "graphic_designer"
        SEO = "seo"
        
        
        
    job_seeker = models.OneToOneField(JobSeeker , on_delete=models.CASCADE)
    file = models.FileField(upload_to='resumes/' , null=True , blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    skills = models.JSONField(default=dict , null=True)
    experience = models.IntegerField()
    education = models.CharField(choices=EducationChoices)
    stack = models.CharField(choices=StackChoices)
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
    