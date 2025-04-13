
# third party imports
from rest_framework import serializers
from rest_framework.validators import ValidationError

# local imports
from .models import Package , PurchasedPackage
from employer.models import Employer
from payment.models import Payment


class PackageSerializer(serializers.ModelSerializer) :
    class Meta :
        model = Package
        exclude = ['user']
        read_only = ['id' , 'created_at']
        
    def validate(self , attrs) : 
        
        package_type = attrs.get('type')
        priority = attrs.get('priority')
        count = attrs.get('count')

        if package_type == "offer":
            if not priority :
                raise ValidationError("priority must be entered")
        if package_type == "resume" and priority == "urgent" :
            raise ValidationError('package can not have priority')
        if package_type == "resume" :
                priority = "normal"
                # if not count :
                #     raise ValidationError("count must be entered")
        # limit the count. admin can not register package with the same count as the active packages if the type , priority are the same
        # package = Package.objects.filter(type=package_type , priority= priority, count=count , active=True).count()
        # if package > 1 :
        #     raise ValidationError("with this count you can only have on active package , deactive the other packages to register this package")
        return attrs

class GetPackageSerializer(serializers.ModelSerializer) :
    class Meta :
        model = Package
        fields = '__all__'



class PurchasePackageSerializer(serializers.ModelSerializer) :
    package = serializers.PrimaryKeyRelatedField(queryset=Package.objects.all())
    # payment = serializers.PrimaryKeyRelatedField(queryset=Payment.objects.all())
    class Meta :
        model = PurchasedPackage
        exclude = ['employer' , 'remaining' , 'active']
    
    # def validate_payment(self , attr) :
    #     user = self.context.get('request').user
    #     if attr.employer.user != user :
    #         raise ValidationError("the payment does not belong to the user")
    #     return attr
    
class GetPurchasedPackageSerializer(serializers.ModelSerializer) :
    class Meta :
        model = PurchasedPackage
        fields = '__all__'