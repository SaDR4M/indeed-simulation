import ast
import json
# third part imports
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
# local
from job_seeker.models import Application 
from employer.models import InterviewSchedule
from employer.utils import employer_exists
from job_seeker.utils import job_seeker_exists
from job_seeker.serializers import GetResumeSerializer
from job_seeker.models import Resume



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
        
        
    def check_conflict(self , interview_pk , time, apply , kind ) :
            
        print(interview_pk)
        # employer conflict with its own time
        employer_conflict = InterviewSchedule.objects.filter(apply__job_opportunity__employer = apply.job_opportunity.employer , apply__status="interview").exclude(pk=interview_pk).filter(employer_time__in = [time])
            
        if employer_conflict.exists() :
            if kind == "employer" :
                return Response(data={"error" : "conflict with its own time" , "fa_error" : "شما مصحاحبه ای با تایم داده شده دارید"} , status=status.HTTP_400_BAD_REQUEST)
            if kind == "job_seeker" :
                return Response(data={"error" : "conflict with its employer time" , "fa_error" :"کافرما در زمان داده شده مصاحبه ای دارد"} , status=status.HTTP_400_BAD_REQUEST)
            
            
        # job seeker conflict with employer time
        job_seeker_conflict = InterviewSchedule.objects.filter(apply__job_seeker = apply.job_seeker , apply__status = "interview").exclude(pk=interview_pk  , status="rejected").filter(job_seeker_time__in = [time])
        
        if job_seeker_conflict.exists() :
            if kind == "employer" :
               return Response(data={"error" : "conflict with job seeker time" , "fa_error" : "کارجو در زمان داده شده مصاحبه ای دارد"}, status=status.HTTP_400_BAD_REQUEST)
            if kind == "job_seeker" : 
             return Response(data={"error" : "conflict with its own time" , "fa_error" : "شما مصحاحبه ای با تایم داده شده دارید"} , status=status.HTTP_400_BAD_REQUEST)
         
         
         
class FilterResumse:
    # def filter_stack(self , resume , stack) :
    #     filtered_resume = resume.object.filter(stack=stack)
    #     serializer = GetResumeSerializer(filtered_resume , many=True)
    #     return serializer
        
    
    # def filter_education(self , resume , education):
    #     filtered_resume = resume.object.filter(stack=stack)
    #     serializer = GetResumeSerializer(filtered_resume , many=True)
    #     return serializer
    
    # def filter_exprience(self , resume , exprience):
    #     filtered_resume = resume.object.filter(stack=stack)
    #     serializer = GetResumeSerializer(filtered_resume , many=True)
    #     return serializer
    
    def filter_resume(self , request) :
               # for filtering the data
        stack = request.GET.get('stack')
        education = request.GET.get('education')
        experience = request.GET.get('experience')
        test = request.GET.get('test')
        skills = request.GET.get('skills')
        
        # check stack and education choices
        if education :
            education_choices = dict(Resume.EducationChoices.choices)
            if education not in education_choices :
                return Response(data={"error" : "education is not valid"} , status=status.HTTP_400_BAD_REQUEST)
        if stack :
            stack_choices = dict(Resume.StackChoices.choices)
            if stack not in stack_choices :
                return Response(data={"error" : "stack is not valid"} , status=status.HTTP_400_BAD_REQUEST)
        # filter resume base on user paramters
        resumes = Resume.objects.all()
        if not resumes.exists() :
            return Response(data={"detail" : "there is no resume"} , status=status.HTTP_404_NOT_FOUND)

        # using Q to apply multiple filter base on the AND 
        # =& its the AND for query = Q(stack="front_end") & Q(education="bachelor")
        # it will be just of single query
        query = Q()
        if stack :
            query &= Q(stack=stack)
        # check education be in list of educations
        if education :
            query &= Q(education=education)
        # 0 is considered as None
        if experience is not None :
            query &= Q(experience__gte=experience)
        # base on the available test
        # list of test id's
        # print(ast.literal_eval(f"{skills}"))
        if test :
            query &= Q(test__in=test)
        # filter base on the skills
        # convert the skill to dict if it is not json
        if skills :
            skills = json.loads(skills)
            for key,value in skills.items() :
                query &= Q(skills__contains={key.lower(): value.lower()})       
            # if isinstance(skills , str) :
                    # skills = ast.literal_eval(f"{skills}")
                  
        resume = resumes.filter(query)
        return resume
        
    
    