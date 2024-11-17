# third party imports
from rest_framework.validators import ValidationError
from rest_framework import serializers

# local import
from employer.models import Employer , JobOpportunity
from package.models import PurchasedPackage

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
            fields = {k : v for k , v in attrs.items() if k != offer_id}
            if not fields :
                raise ValidationError("at least one field must be entered")
        
        return attrs
    
        
