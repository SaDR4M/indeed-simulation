
# third party imports
from rest_framework import serializers

# local imports
from .models import Package , PurchasedPackage
from employer.models import Employer
from payment.models import Payment


class PackageSerializer(serializers.ModelSerializer) :
    class Meta :
        model = Package
        fields = '__all__'

class PurchasePackageSerializer(serializers.ModelSerializer) :
    package = serializers.PrimaryKeyRelatedField(queryset=Package.objects.all())
    payment = serializers.PrimaryKeyRelatedField(queryset=Payment.objects.all())
    # employer = serializers.PrimaryKeyRelatedField(queryset=Employer.objects.all())
    class Meta :
        model = PurchasedPackage
        # fields = '__all__'
        exclude = ['employer']