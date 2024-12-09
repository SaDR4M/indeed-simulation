# third party imports
from urllib import request
from rest_framework import serializers

# local imports
from .models import Payment
from employer.models import Employer

class PaymentSerializer(serializers.ModelSerializer) :
    # employer = serializers.PrimaryKeyRelatedField(queryset = Employer.objects.all())
    checkout_at = serializers.DateTimeField(format="%Y-%m-%d , %H:%M:%S" , required=False)
    class Meta : 
        model = Payment
        exclude = ['employer' , 'authority' , 'payment_id' , 'amount']
    
        