from rest_framework import serializers
# local imports
from employer.models import Employer

class GetEmployerSerializer(serializers.ModelSerializer) :
    class Meta :
        model = Employer
        fields = '__all__'
