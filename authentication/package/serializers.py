
# third party imports
from rest_framework import serializers
from rest_framework.validators import ValidationError

# local imports
from .models import Package , PurchasedPackage
from employer.models import Employer
from payment.models import Payment


class PackageSerializer(serializers.ModelSerializer) :
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S' , required=False)
    class Meta :
        model = Package
        exclude = ['user']
        read_only = ['id']
        
    def validate(self , attrs) : 
        
        package_type = attrs.get('type')
        priority = attrs.get('priority')
        count = attrs.get('count')
        if package_type == 0:
            if not priority :
                raise ValidationError("priority must be entered")
        if package_type == 1 :
            if not count :
                raise ValidationError("count must be entered")
        if package_type == 1 and priority == 1 :
            raise ValidationError('resume can not have priority')
        return attrs

class PurchasePackageSerializer(serializers.ModelSerializer) :
    package = serializers.PrimaryKeyRelatedField(queryset=Package.objects.all())
    payment = serializers.PrimaryKeyRelatedField(queryset=Payment.objects.all())
    class Meta :
        model = PurchasedPackage
        exclude = ['employer']
    
    def validate_payment(self , attr) :
        user = self.context.get('request').user
        if attr.employer.user != user :
            raise ValidationError("the payment does not belong to the user")
        return attr
    
 