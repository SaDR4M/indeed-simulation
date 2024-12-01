# third part imports
from rest_framework.response import Response
from rest_framework import status
# local
from job_seeker.models import Application 
from employer.models import InterviewSchedule
from employer.utils import employer_exists
from job_seeker.utils import job_seeker_exists

class InterviewScheduleMixin:
    def check_apply_and_permissions(self , apply_id  ,user , kind):
            
        if not apply_id :
            return Response(data={"error" : "apply id must be entered"} , status=status.HTTP_400_BAD_REQUEST)
        
        try :
            apply = Application.objects.get(pk=apply_id)
            employer = apply.job_opportunity.employer
            
        except Application.DoesNotExist :
            return Response(data={"error" : "there is no apply with this id" , "fa_error" : "موقعیت شغلی با این مشخصات پیدا نشد"} , status=status.HTTP_404_NOT_FOUND)
        
        if kind == "employer" :
            employer = employer_exists(user)  
            if not employer :
                return Response(data={"error" : "employer does not exists"} , status=status.HTTP_404_NOT_FOUND)
            
            if not employer.user.has_perm("change_interviewschedule", apply ) :
                return Response(data={"error" : "user does not have permission"} , status=status.HTTP_403_FORBIDDEN)

        if kind == "job__seeker" : 
            job_seeker = job_seeker_exists(user)
            
            if not job_seeker :
                return Response(data={"error" : "job_seeker does not exists"} , status=status.HTTP_404_NOT_FOUND)

        
            if not job_seeker.user.has_perm("change_interviewschedule", apply ) :
                return Response(data={"error" : "user does not have permission"} , status=status.HTTP_403_FORBIDDEN)
        
               
        return apply

        

        
     
    def check_interview(self , apply) : 
        try :
            interview = InterviewSchedule.objects.get(apply=apply)
        except InterviewSchedule.DoesNotExist :
            return Response(data={"error" : "interview schedule does not exists"} , status=status.HTTP_404_NOT_FOUND)
        
        if interview.status == "approved" :
            return Response(data={"error" : "schedule can not be changed"} , status=status.HTTP_400_BAD_REQUEST)
        return interview
        
        
        
    def check_conflict(self , interview_pk , time, apply ) :

        # employer conflict with its own time
        employer_conflict = InterviewSchedule.objects.filter(apply__job_opportunity__employer = apply.job_opportunity.employer , apply__status="interview").exclude(pk=interview_pk , status="rejected").filter(employer_time__in = [time])
            
        if employer_conflict.exists() :
            return Response(data={"error" : "conflict with its own time" , "fa_error" : "شما مصحاحبه ای با تایم داده شده دارید"} , status=status.HTTP_400_BAD_REQUEST)
        # job seeker conflict with employer time
        job_seeker_conflict = InterviewSchedule.objects.filter(apply__job_seeker = apply.job_seeker , apply__status = "interview").exclude(pk=interview_pk  , status="rejected").filter(job_seeker_time__in = [time])
        
        if job_seeker_conflict.exists() :
            return Response(data={"error" : "conflict with job seeker time" , "fa_error" : "کارجو/کارفرما در زمان داده شده مصاحبه ای دارد"}, status=status.HTTP_400_BAD_REQUEST)
