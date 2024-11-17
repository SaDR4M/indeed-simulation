# third party imports
from rest_framework import serializers
from rest_framework.parsers import MultiPartParser, FormParser
# local imports
from .models import JobSeeker , Resume , Application

class JobSeekerSerializer(serializers.ModelSerializer):
    class Meta :
        model = JobSeeker
        exclude = ['user']
        # fields = '__all__'

class ResumeSerializer(serializers.ModelSerializer):
    file = serializers.FileField(required=False)
    class Meta :
        model = Resume
        exclude = ['job_seeker']
        # fields = "__all__"

class ApplicationSerializer(serializers.ModelSerializer):
    id = serializers.CharField(required=True)
    class Meta:
        model = Application
        exclude = ['job_seeker' , 'job_opportunity']
