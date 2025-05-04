# third party imports
from django.urls import include
from rest_framework.validators import ValidationError
from rest_framework import serializers
from rest_framework.validators import ValidationError
# local import
from employer.models import Employer, JobOpportunity, ViewedResume, InterviewSchedule, ViewedAppliedResume
from package.models import Package
from job_seeker.models import Resume , Application 
from location.serializer import CitiesSerializer , ProvincesSerializer
from location.models import Cities , Provinces
from manager.serializer import TechnologyCategoryShowSerializer


class EmployerSerializer(serializers.ModelSerializer) :
    city = CitiesSerializer()
    province = ProvincesSerializer()
    class Meta :
        model = Employer
        exclude = ['user']

class UpdateEmployerSerializer(serializers.ModelSerializer) :
    province_id = serializers.IntegerField(required=False)
    city_id = serializers.IntegerField(required=False)
    class Meta :
        model = Employer
        exclude = ['user' , 'city' , 'province']     
        
    def update(self , instance , validated_data) : 
        try :
            city = validated_data.get("city_id")
            province = validated_data.get("province_id")
            instance.city = Cities.objects.get(id=city , province_id = province)
        except : 
            raise ValidationError("city and province must be matched")
        try :
            province = validated_data.get("province_id")
            instance.province = Provinces.objects.get(id=province)
        except :
            pass
        super().update(instance , validated_data)
        return instance
        
class JobOpportunityUpdateSerializer(serializers.ModelSerializer) :
    class Meta :
        model = JobOpportunity
        exclude = ['employer' ,'active'  , 'status']
        
class JobOpportunitySerializer(serializers.ModelSerializer) :
    # package_purchase_id = serializers.PrimaryKeyRelatedField(queryset=PurchasedPackage.objects.all())
    class Meta :
        model = JobOpportunity
        exclude = ['employer' , 'province', 'city' , 'active' , 'status' , 'stack']
    
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
    stack = TechnologyCategoryShowSerializer(many=True)
    priority = serializers.SerializerMethodField()
    class Meta :
        model = JobOpportunity
        fields = '__all__'
        
    def get_priority(self , instance) :
        if instance.package :
            return instance.package.priority
   
    
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