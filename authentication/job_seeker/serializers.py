# third party imports
from rest_framework import serializers
# local imports
from .models import JobSeeker , Resume , Application

class JobSeekerSerializer(serializers.ModelSerializer):
    class Meta :
        model = JobSeeker
        exclude = ['user']
        # fields = '__all__'

class ResumeSerializer(serializers.ModelSerializer):
    class Meta :
        model = Resume
        exclude = ['job_seeker']
        # fields = "__all__"
