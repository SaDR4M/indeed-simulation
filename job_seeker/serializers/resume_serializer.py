# third party imports
from rest_framework import serializers
# local imports
from job_seeker.models import  Resume



class GetResumeSerializer(serializers.ModelSerializer) :
    class Meta :
        model = Resume
        fields = '__all__'
        
        
class ResumeSerializer(serializers.ModelSerializer):
    file = serializers.FileField(required=False)
    class Meta :
        model = Resume
        exclude = ['job_seeker' , 'test']