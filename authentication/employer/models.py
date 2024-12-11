
from django.db import models
from django.contrib.auth import get_user_model
import datetime
# local import
from account.models import User , Cities , Countries , States
from common.mixins import GenderMixin
# Create your models here.

# extra information about the employer
# TODO add state to it
class Employer(GenderMixin):

    user = models.OneToOneField(User, on_delete=models.CASCADE , related_name="employer")
    title = models.CharField(max_length=100)
    address = models.CharField(max_length=250)
    id_number = models.CharField(max_length=25)
    postal_code = models.CharField(max_length=25)
    created_at = models.DateTimeField(auto_now_add=True)
    country = models.ForeignKey(Countries , related_name="country_employers" , on_delete=models.CASCADE)
    state = models.ForeignKey(States , related_name="state_employers" , on_delete=models.CASCADE)
    city = models.ForeignKey(Cities , related_name="city_emoployers" , on_delete=models.CASCADE)

    
# opportunity that employer makes
# TODO add state to it
class JobOpportunity(GenderMixin):
        
    class OfferStatus(models.TextChoices) :
        REGISTRED = "registered" , "Registered"
        CONFIRMED = "approved" , "Approved"
        CANCELED = "canceled" , "Canceled"
        EXPIRED = "expired" , "Expired"
        
    employer = models.ForeignKey("employer.Employer" , on_delete=models.CASCADE , related_name="job_opportunities")
    active = models.BooleanField(default=False)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    status = models.CharField(choices=OfferStatus , default=OfferStatus.REGISTRED)
    created_at = models.DateTimeField(auto_now_add=True)
    country = models.ForeignKey(Countries , related_name="job_offers" , on_delete=models.CASCADE)
    state = models.ForeignKey(States , related_name="job_states" , on_delete=models.CASCADE)
    city = models.ForeignKey(Cities , related_name="job_offers" , on_delete=models.CASCADE)
    # i changed the data type of this column manually in the DB
    expire_at = models.DateTimeField()

# basket package
class EmployerCart(models.Model) :
    employer =  models.ForeignKey("employer.Employer" , on_delete=models.CASCADE ,  related_name="carts")
    active = models.BooleanField(default=True)
    added_at = models.DateTimeField(auto_now_add=True)
    
# basket items
class EmployerCartItem(models.Model) :
    cart = models.ForeignKey(EmployerCart  , on_delete=models.CASCADE , related_name="cart_items")
    package = models.ForeignKey("package.Package" , on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

class EmployerOrder(models.Model) :
    
    class OrderStatus(models.TextChoices) :
        COMPLETED = "completed"
        PENDING = "pending"
        FAILED = "failed"
        REFUNDED = "refunded"
        
    employer = models.ForeignKey("employer.Employer" , on_delete=models.CASCADE , related_name="orders")
    payment = models.OneToOneField("payment.Payment" , on_delete=models.CASCADE , related_name="order")
    status = models.CharField(choices=OrderStatus , default=OrderStatus.PENDING)
    order_at = models.DateTimeField(auto_now_add=True)
    order_id = models.IntegerField()

class EmployerOrderItem(models.Model) :
    order = models.ForeignKey(EmployerOrder , on_delete=models.CASCADE , related_name="order_items")
    package = models.ForeignKey("package.Package" , on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)


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
    interview_time= models.DateTimeField(null=True , blank=True)
    status = models.CharField(choices=InterViewStatus , default=InterViewStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)


    