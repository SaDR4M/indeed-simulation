# third party imports
from rest_framework import serializers
# local imports
from job_seeker.models import Application
from employer.models import InterviewSchedule



class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        exclude = ['job_seeker' , 'job_opportunity' , 'status']


class ChangeJobSeekerInterviewScheduleSerializer(serializers.ModelSerializer) :
    job_seeker_time = serializers.DateTimeField(required=False)
    class Meta :
        model = InterviewSchedule
        exclude = ['status' , 'employer_time']