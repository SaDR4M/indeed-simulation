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
from account.models import Cities , Countries , States


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
   
   
class CountryCityIdMixin:
    
    def country_and_city_id(self , request) :
        
        city = request.data.get('city') 
        if not city :
            return Response(data={"error" : "city must be entered"} , status=status.HTTP_400_BAD_REQUEST)
        
        state = request.data.get('state') 
        if not state :
            return Response(data={"error" : "state must be entered"} , status=status.HTTP_400_BAD_REQUEST)
        
        country = request.data.get('country')
        if not country :
            return Response(data={"error" : "country must be entered"} , status=status.HTTP_400_BAD_REQUEST)
        
        data = {}
        try :
            country = Countries.objects.get(name__iexact=country.lower())
            data['country'] = country
        except Countries.DoesNotExist :
            return Response(data={"error" : "country does not exists"} , status=status.HTTP_404_NOT_FOUND)
        
        try :
            state = States.objects.get(country=country , name__iexact=state.lower())
            data['state'] = state
        except States.DoesNotExist :
            return Response(data={"error" : "state does not exists"} , status=status.HTTP_404_NOT_FOUND)
        
        
        try :
            city = Cities.objects.get(country=country , state=state ,  name__iexact=city.lower())
            data['city'] = city
        except Cities.DoesNotExist :
            return Response(data={"error" : "city does not exists"} , status=status.HTTP_400_BAD_REQUEST)
        
        return data
       
   
   
         
         
         
class FilterResumseMixin:
    
    def filter_resume(self) :
        # for filtering the data
        allowed_filters_dict = {
            "job_seeker_id": {"model_field": "job_seeker", "lookup": "exact"},
            "experience_min": {"model_field": "experience", "lookup": "gte"},
            "experience_max": {"model_field": "experience", "lookup": "lte"},
            "education": {"model_field": "education", "lookup": "exact"},
            "stack": {"model_field": "stack", "lookup": "exact"},
            "updated_last_month": {"model_field": "updated_at", "lookup": "lte"},
            "updated_last_year": {"model_field": "updated_at", "lookup": "lte"},
            "skills": {"model_field": "skills", "lookup": "contains"},
            "country": {"model_field": "job_seeker__country__name", "lookup": "iexact"},
            "city": {"model_field": "job_seeker__city__name", "lookup": "iexact"},
        }

         
        resumes = Resume.objects.all()
        query = Q()
        or_query = Q()
        parameters = self.request.query_params
        for parameter in parameters : 
            filter_match = allowed_filters_dict.get(parameter)
            if filter_match:
                value = self.request.query_params.get(parameter)
                values = value.split(',')    
                # if len(values) > 1 and parameter in ['skills ' , 'education' , 'stack'] :  
                if parameter in ['skills' , 'education' , 'stack'] :
                    try :
                        if parameter == "skills" :
                            skills = json.loads(value)
                            for key,value in skills.items() :
                                field = f"{filter_match['model_field']}__{filter_match['lookup']}"
                                query |= Q(**{field : {key.lower(): value.lower()}})
                    except :
                        return Response(data={"error" : "error occured for the skills"} , status=status.HTTP_400_BAD_REQUEST)
                    else :
                        for value in values : 
                            field = f"{filter_match['model_field']}"
                            or_query |=  Q(**{field : value}) 
                else :
                    field = (f"{filter_match['model_field']}__{filter_match['lookup']}")
                    query &= Q(**{field : value})
            else :
                return Response(data={"error" : f"{parameter} is not valid"} , status=status.HTTP_400_BAD_REQUEST)
        query &= or_query
        resume = resumes.filter(query)
        return resume
        