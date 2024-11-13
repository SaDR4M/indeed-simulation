from rest_framework import serializers
# local import
from employer.models import Employer , JobOpportunity


class EmployerSerializer(serializers.ModelSerializer) :
    class Meta :
        model = Employer
        exclude = ['user']

class JobOpportunitySerializer(serializers.ModelSerializer) :
    class Meta :
        model = JobOpportunity
        exclude = ['employer']

