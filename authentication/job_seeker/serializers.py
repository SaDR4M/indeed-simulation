# third party imports
from rest_framework import serializers
from rest_framework.parsers import MultiPartParser, FormParser
# local imports
from .models import JobSeeker , Resume , Application , Test , QuestionAndAnswers
from employer.models import InterviewSchedule



class JobSeekerSerializer(serializers.ModelSerializer):
    class Meta :
        model = JobSeeker
        exclude = ['user']
        # fields = '__all__'

class ResumeSerializer(serializers.ModelSerializer):
    file = serializers.FileField(required=False)
    class Meta :
        model = Resume
        exclude = ['job_seeker' , 'test']
        # fields = "__all__"
class GetResumeSerializer(serializers.ModelSerializer) :
    class Meta :
        model = Resume
        fields = '__all__'


class ApplicationSerializer(serializers.ModelSerializer):
    id = serializers.CharField(required=True)
    class Meta:
        model = Application
        exclude = ['job_seeker' , 'job_opportunity' , 'status']


class ChangeInterviewJobSeekerScheduleSerializer(serializers.ModelSerializer) :
    job_seeker_time = serializers.DateTimeField(required=False)
    class Meta :
        model = InterviewSchedule
        exclude = ['status' , 'employer_time']
        
        
        
class TestSerializer(serializers.ModelSerializer) :
    
    class Meta :
        model = Test
        exclude = ['user']
        
    def update(self , instance , validated_data) :
        
        restriced_fields = ['created_at' , 'deleted_at']
        for field in restriced_fields :
            if field in validated_data :
                raise serializers.ValidationError({field : "this field can not be updated"})
        return super().update(instance , validated_data)


class QuestionAndAnswersSerializer(serializers.ModelSerializer) :
    
    class Meta :
        model = QuestionAndAnswers
        exclude = ['test' , 'user']
    
    
    def update(self , instance , validated_data) :
        
        restriced_fields = ['created_at' , 'deleted_at']
        for field in restriced_fields :
            if field in validated_data :
                raise serializers.ValidationError({field : "this field can not be updated"})
        return super().update(instance , validated_data)