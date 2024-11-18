# third party imports
from django.urls import include
from rest_framework.validators import ValidationError
from rest_framework import serializers

# local import
from employer.models import Employer , JobOpportunity , ViewedResume
from job_seeker.models import Resume

class EmployerSerializer(serializers.ModelSerializer) :
    class Meta :
        model = Employer
        exclude = ['user']

class JobOpportunitySerializer(serializers.ModelSerializer) :
    # package_purchase_id = serializers.PrimaryKeyRelatedField(queryset=PurchasedPackage.objects.all())
    class Meta :
        model = JobOpportunity
        exclude = ['employer']
    

    def validate(self , attrs) :
        if self.partial :
            offer_id = attrs.get('offer_id')
            status = attrs.get('status')
            fields = {k : v for k , v in attrs.items() if k != offer_id}
            if not fields :
                raise ValidationError("at least one field must be entered")
            if status == "expired" or status == "canceled":
                attrs['active'] = False
            else :
                attrs['active'] = True
        return attrs
    
   
    
class ViewedResumeSerializer(serializers.ModelSerializer) :
    resume = serializers.PrimaryKeyRelatedField(queryset=Resume.objects.all())
    class Meta :
        model = ViewedResume
        exclude = ["employer"]
        

        

