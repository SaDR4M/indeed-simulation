# third party imports
from rest_framework import serializers

# local imports
from .models import Payment
from employer.models import Employer

class PaymentSerializer(serializers.ModelSerializer) :
    employer = serializers.PrimaryKeyRelatedField(queryset = Employer.objects.all())
    class Meta : 
        model = Payment
        # exclude = ['employer']
        fields = '__all__'
        