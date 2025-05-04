
from django.db import models
from django.contrib.auth import get_user_model
import datetime
# local import
from account.models import User
from location.models import Cities , Provinces
from core.mixins import GenderMixin
from core.choices import CooperationChoices , ExperienceChoices , WorkModeChoices
from manager.models import TechnologyCategory
# Create your models here.

# extra information about the employer
class Employer(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE , related_name="employer")
    company_email = models.EmailField(max_length=512 , null=False , blank=False)
    company_name = models.CharField(max_length=100 , help_text="company name")
    address = models.CharField(max_length=250)
    id_number = models.CharField(max_length=25 , help_text="company register number")
    postal_code = models.CharField(max_length=25)
    created_at = models.DateTimeField(auto_now_add=True)
    province = models.ForeignKey(Provinces , related_name="state_employers" , on_delete=models.CASCADE , default=8 , help_text="province of the company . default is Tehran")
    city = models.ForeignKey(Cities , related_name="city_emoployers" , on_delete=models.CASCADE , default=301 , help_text="city of the company . default is Tehran")
    is_banned = models.BooleanField(default=False)
    banned_by = models.ForeignKey(User, related_name="banned_employers", on_delete=models.CASCADE, null=True, blank=True)
    banned_at = models.DateTimeField(null=True , blank=True)
    banned_description = models.CharField(max_length=255 , null=True , blank=True)
    
# opportunity that employer makes
class JobOpportunity(models.Model):
        
    class OfferStatus(models.TextChoices) :
        REGISTRED = "registered" , "Registered"
        CONFIRMED = "approved" , "Approved"
        CANCELED = "canceled" , "Canceled"
        EXPIRED = "expired" , "Expired"
    
    class GenderChoices(models.TextChoices) :
        MALE = "male"
        FEMALE = "female"
        UNISEX = "unisex"
                
    employer = models.ForeignKey(
        "employer.Employer" ,
        on_delete=models.CASCADE ,
        related_name="job_opportunities"
    )
    active = models.BooleanField(
        default=False
    )
    deleted = models.BooleanField(
        default=False
    )
    title = models.CharField(
        max_length=100
    )
    description = models.TextField(
        max_length=500
    )
    stack_description = models.TextField(
        max_length=500,
        null=True,
        blank=True
    )
    status = models.CharField(
        choices=OfferStatus ,
        default=OfferStatus.REGISTRED
    )
    updated_by_admin = models.ForeignKey(
        "account.User" ,
        on_delete=models.CASCADE ,
        null=True , blank=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True
    )
    province = models.ForeignKey(Provinces , 
        related_name="job_states" ,
        on_delete=models.CASCADE , 
        help_text="province of the offer . default is Tehran"
    )
    city = models.ForeignKey(Cities , 
        related_name="job_offers" , 
        on_delete=models.CASCADE , 
        default=301 , 
        help_text="city of the offer . default is Tehran"
    )
    stack = models.ManyToManyField(
        TechnologyCategory ,
        related_name="offers"
    )
    gender = models.CharField(
        choices=GenderChoices ,
        default=GenderChoices.UNISEX
    )
    experience = models.CharField(
        choices=ExperienceChoices,
        default=ExperienceChoices.JUNIOR
    )
    cooperation = models.CharField(
        choices=CooperationChoices,
        default=CooperationChoices.FULLTIME
    )
    work_mode = models.CharField(
        choices=WorkModeChoices,
        default=WorkModeChoices.ONSITE
    )
    package = models.ForeignKey(
        "package.Package",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="package_job_opportunities"
    )
    # i changed the data type of this column manually in the DB
    expire_at = models.DateTimeField()


class ViewedResume(models.Model) :
    resume = models.ForeignKey("job_seeker.Resume" , on_delete=models.CASCADE) 
    employer = models.ForeignKey("employer.Employer" , on_delete=models.CASCADE)
    seen_at = models.DateTimeField(auto_now_add=True)
    
class ViewedAppliedResume(models.Model) :
    resume = models.ForeignKey('job_seeker.Resume' , on_delete=models.CASCADE)
    job_offer = models.ForeignKey("employer.JobOpportunity" , on_delete=models.CASCADE)
    seen_at = models.DateTimeField(auto_now_add=True)
    
    

class InterviewSchedule(models.Model) :
    class InterViewStatus(models.TextChoices) :
        PENDING = "pending"
        APPROVED = "approved"
        REJECTED_BY_EMPLOYER = "rejected_by_employer"
        REJECTED_BY_JOBSEEKER = 'rejected_by_jobseeker'
        CONFLICT = "conflict"
        
    apply = models.OneToOneField("job_seeker.Application" , on_delete=models.CASCADE , related_name="schedules")
    job_seeker_time = models.DateTimeField(null=True , blank=True)
    employer_time = models.DateTimeField(null=True , blank=True)
    interview_time = models.DateTimeField(null=True , blank=True)
    status = models.CharField(choices=InterViewStatus , default=InterViewStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)


    