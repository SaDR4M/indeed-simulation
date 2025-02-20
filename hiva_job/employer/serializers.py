# third party imports
from django.urls import include
from rest_framework.validators import ValidationError
from rest_framework import serializers

# local import
from employer.models import Employer, JobOpportunity, ViewedResume, InterviewSchedule, ViewedAppliedResume
from package.models import Package
from job_seeker.models import Resume , Application 

class EmployerSerializer(serializers.ModelSerializer) :
    class Meta :
        model = Employer
        exclude = ['user'  , 'province', 'city']
        

class JobOpportunitySerializer(serializers.ModelSerializer) :
    # package_purchase_id = serializers.PrimaryKeyRelatedField(queryset=PurchasedPackage.objects.all())
    class Meta :
        model = JobOpportunity
        exclude = ['employer' , 'province', 'city']
    
    def validate(self , attrs) :
        if self.partial :
            offer_id = attrs.get('offer_id')
            status = attrs.get('status')
            fields = {k : v for k , v in attrs.items() if k != offer_id}
            if not fields :
                raise ValidationError("at least one field must be entered")
            # if status == "expired" or status == "canceled":
            #     attrs['active'] = False
            # else :
            #     attrs['active'] = True
        return attrs
    
    
class GetJobOpportunitySerializer(serializers.ModelSerializer) :
    class Meta :
        model = JobOpportunity
        fields = '__all__'
   
    
class ViewedResumeSerializer(serializers.ModelSerializer) :
    resume = serializers.PrimaryKeyRelatedField(queryset=Resume.objects.all())
    class Meta :
        model = ViewedResume
        exclude = ["employer"]
   
        
class GetViewedResumeSerializer(serializers.ModelSerializer) :
    class Meta:
        model = ViewedResume
        fields = '__all__'        
      
        
class AppliedViewedResumeSerializer(serializers.ModelSerializer) :
    class Meta :
        model = ViewedAppliedResume
        exclude = ['job_offer' , 'resume']
        
class GetAppliedViewedResumeSerializer(serializers.ModelSerializer) :
    class Meta :
        model = ViewedAppliedResume
        fields = '__all__'


class ChangeApllyStatusSerializer(serializers.ModelSerializer) :
    # id = serializers.PrimaryKeyRelatedField(queryset=Application.objects.all())
    class Meta :
        model = Application
        fields = ["status"]
    

class InterviewScheduleSerializer(serializers.ModelSerializer) :
    class Meta:
        model = InterviewSchedule
        fields = '__all__'

# ChangeEmployerInterviewScheduleSerializer
class ChangeEmployerInterviewScheduleSerializer(serializers.ModelSerializer) :
    employer_time = serializers.DateTimeField(required=False)
    class Meta :
        model = InterviewSchedule
        exclude = ['status' , 'job_seeker_time']