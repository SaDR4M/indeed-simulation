
# third party imports
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK , HTTP_400_BAD_REQUEST , HTTP_404_NOT_FOUND
# local imports
from employer.serializers import (InterviewScheduleSerializer)
                          
from employer.models import InterviewSchedule
from employer.utils import employer_exists , change_interview_schedule
from employer.mixins import InterviewScheduleMixin , FilterInterviewScheduleMixin
from employer.docs import (
    interview_schedule_get_doc,
    interview_schedule_post_doc
)
# Create your views here.

class EmployerInterviewSchedule(APIView , InterviewScheduleMixin , FilterInterviewScheduleMixin) :

    # list of employer interview schedule
    @interview_schedule_get_doc
    def get(self , request):
        """get the employer inteview schedule and filter the data"""
        user = request.user
        employer = employer_exists(user)
        if not employer :
            return Response(data={"error" : "employer does not exists"} ,status=HTTP_404_NOT_FOUND )
        # get the schedule base on employer
        interviews = InterviewSchedule.objects.filter(apply__job_opportunity__employer = employer ).exclude(status__in = ["rejected_by_employer" , "rejected_by_jobseeker"])
        
        filtered_data = self.filter_interview(interviews)
        if isinstance(filtered_data , Response) :
            return filtered_data            
        
        serializer = InterviewScheduleSerializer(filtered_data , many=True)
        return Response(data={"data" : serializer.data} , status=HTTP_200_OK)
    
    @interview_schedule_post_doc
    def patch(self , request) :
        user = request.user
        
        apply_id = request.data.get("apply_id")
        employer_time = request.data.get("employer_time")
        # check employer has permission for this apply or not
        apply = self.check_apply_and_permissions(apply_id ,user , "employer" )
        if isinstance(apply , Response) :
            return apply
        # get interview data    
        interview = self.check_interview(apply)
        if isinstance(interview , Response) :
            return interview
        # check conflict times between job seeker time or its own interviews time
        conflict = self.check_conflict(interview.pk , employer_time , apply , "employer")
        if isinstance(conflict , Response) :
            return conflict

        # update the interview schedule
        response = change_interview_schedule()
        return response
        