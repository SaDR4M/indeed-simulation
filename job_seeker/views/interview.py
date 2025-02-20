
# third party imports
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

# local imports
from job_seeker.serializers import  ChangeJobSeekerInterviewScheduleSerializer 
from employer import utils
from employer.serializers import InterviewScheduleSerializer
from employer.models import InterviewSchedule  
from employer.mixins import InterviewScheduleMixin, FilterInterviewScheduleMixin 
from job_seeker.docs import (
    interview_schedule_get_doc,
    interview_schedule_patch_doc
)

# Create your views here.

class JobSeekerInterviewSchedule(APIView , InterviewScheduleMixin , FilterInterviewScheduleMixin) : 

    @interview_schedule_get_doc
    def get(self , request):
        user = request.user
        job_seeker = utils.job_seeker_exists(user)
        if not job_seeker :
            return Response(data={"error" : "employer does not exists"} ,status=status.HTTP_404_NOT_FOUND )
        # get the schedule base on employer
        interviews = InterviewSchedule.objects.filter(apply__job_seeker = job_seeker ).exclude(status__in = ["rejected_by_employer" , "rejected_by_jobseeker"])
        
        for interview in interviews :
            if not user.has_perm("view_interviewschedule",interview):
                return Response(data={"error" : "user does not have permission to do this action"} , status=status.HTTP_403_FORBIDDEN)
        
        filtered_data = self.filter_interview(interviews)
        if isinstance(filtered_data , Response) :
            return filtered_data
        
        serializer = InterviewScheduleSerializer(filtered_data , many=True)
        return Response(data={"data" : serializer.data} , status=status.HTTP_200_OK)
    
    @interview_schedule_patch_doc
    def patch(self , request) :
        user = request.user

        job_seeker_time = request.data.get('job_seeker_time')
        apply_id = request.data.get("apply_id")
        
        apply = self.check_apply_and_permissions(apply_id , user , kind="job_seeker")
        if isinstance(apply , Response) :
            return apply
        
        interview = self.check_interview(apply)
        if isinstance(interview , Response) :
            return interview
        
        conflict = self.check_conflict(interview.pk , job_seeker_time , apply , "job_seeker")
        if isinstance(conflict , Response) :
            return conflict

        
        
        serializer = ChangeJobSeekerInterviewScheduleSerializer(interview ,data=request.data , partial=True)
        if serializer.is_valid() :  
            job_seeker_time = serializer.validated_data['job_seeker_time']
            employer_time = interview.employer_time
            if employer_time :
                if employer_time == job_seeker_time :
                    serializer.validated_data['status'] = 'approved'
                    serializer.validated_data['interview_time'] = employer_time
                if job_seeker_time != employer_time :
                    print("Test3")
                    serializer.validated_data['status'] = 'rejected_by_jobseeker'
                    
            serializer.save()
            return Response(data={"success" : True ,"data" : serializer.data ,"interview_time" :  interview.interview_time } , status=status.HTTP_200_OK)
        return Response(data={"errors" : serializer.errors} , status=status.HTTP_400_BAD_REQUEST)
