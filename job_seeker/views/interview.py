
# third party imports
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

# local imports

from job_seeker.utils import change_interview_schedule
from employer.serializers import InterviewScheduleSerializer
from employer.models import InterviewSchedule  
from employer.mixins import InterviewScheduleMixin, FilterInterviewScheduleMixin 
from job_seeker.decorators import job_seeker_required
from job_seeker.docs import (
    interview_schedule_get_doc,
    interview_schedule_patch_doc
)

# Create your views here.

class JobSeekerInterviewSchedule(APIView , InterviewScheduleMixin , FilterInterviewScheduleMixin) : 


    @interview_schedule_get_doc
    @job_seeker_required
    def get(self , request):
        """Get list of job seeker's interviews schedule"""
        user = request.user
        job_seeker = request.job_seeker
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
        """Update interview schedule"""
        user = request.user

        job_seeker_time = request.data.get('job_seeker_time')
        apply_id = request.data.get("apply_id")
        # check user has permission for this job application
        apply = self.check_apply_and_permissions(apply_id , user , kind="job_seeker")
        if isinstance(apply , Response) :
            return apply
        # check if there is interview schedule or not
        interview = self.check_interview(apply)
        if isinstance(interview , Response) :
            return interview
        # check conflict with job seeker time or employer time
        conflict = self.check_conflict(interview.pk , job_seeker_time , apply , "job_seeker")
        if isinstance(conflict , Response) :
            return conflict
        # change the interview schedule
        response = change_interview_schedule(request , interview)
        return response
