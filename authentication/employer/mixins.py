import ast
import json
from datetime import datetime , timedelta   
from dateutil.relativedelta import relativedelta
# third part imports
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from django.db import models
# local
from job_seeker.models import Application 
from employer.models import InterviewSchedule , Employer
from employer.utils import employer_exists
from job_seeker.utils import job_seeker_exists
from job_seeker.serializers import GetResumeSerializer 
from job_seeker.models import Resume
from account.models import Cities , Countries , States
from common.mixins import GenderFilterMixin , LocationFilterMixin , CreationTimeFilterMixin
from .models import JobOpportunity


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
       
   
   
         
         


class FilterResumeMixin:
    def get_date_range_query(self, field, days):
        today = datetime.now()
        if int(days) > 365:
            raise ValueError("Days cannot exceed 365.")
        last_date = today - timedelta(days=days)
        return Q(**{f"{field}__range": [last_date, today]})
    
    def get_age_range_query(self , field , min_age , max_age) :
        print(min_age , max_age)
        today = datetime.now().date()
        if max_age > 100 or min_age < 10:
            raise ValueError("age cannot be less than 10 or more than 100")
        max_birthday_date = today - relativedelta(years=int(max_age))
        min_birthday_date = today - relativedelta(years=int(min_age))
        print(type(max_birthday_date) , min_birthday_date)
        return Q(**{f"{field}__range": [max_birthday_date , min_birthday_date ]})
    
    
    
    def filter_resume(self):
        
        """list of filters that are allowed"""
        allowed_filters_dict = {
            "experience_min": {"model_field": "experience", "lookup": "gte"},
            "experience_max": {"model_field": "experience", "lookup": "lte"},
            "education": {"model_field": "education", "lookup": "exact"},
            "stack": {"model_field": "stack", "lookup": "exact"},
            "gender" : {"model_field" : "job_seeker__gender" , "lookup" : "exact"},
            "age" : {"model_field" : "job_seeker__birthday" , "lookup" : "gte"},
            "skills": {"model_field": "skills", "lookup": "contains"},
            "country": {"model_field": "job_seeker__country__name", "lookup": "iexact"},
            "state": {"model_field": "job_seeker__state__name", "lookup": "iexact"},
            "city": {"model_field": "job_seeker__city__name", "lookup": "iexact"},
        }

        resumes = Resume.objects.all()
        query = Q()
        or_query = Q()
        parameters = self.request.query_params

        for parameter,value in parameters.items():
            print(parameter)
            filter_match = allowed_filters_dict.get(parameter)
            if not filter_match:
                return Response(data={"error": f"{parameter} is not valid"}, status=status.HTTP_400_BAD_REQUEST)
        
            
            if parameter in ['age'] :
                try :
                    field = filter_match['model_field']
                    # TODO add error handling for the type of the value to be array with isinstance
                    value = value.split(',')
                    if len(value) == 2 :
                        min_age = int(value[0].strip()) 
                        max_age = int(value[1].strip())
                    else :
                        raise ValueError("min_age and max_age must be entered")
                    query &= self.get_age_range_query(field , min_age , max_age)
                except Exception as e:
                    return Response(data={"error" : str(e)} , status=status.HTTP_400_BAD_REQUEST)
            
            if parameter in ['skills', 'education', 'stack']:
                try:
                    if parameter == "skills":
                        skills = json.loads(value)
                        for key, value in skills.items():
                            field = f"{filter_match['model_field']}__{key}__{filter_match['lookup']}"
                            or_query |= Q(**{field: value.lower()})
                    else:
                        values = value.split(',')
                        for val in values:
                            field = filter_match['model_field']
                            or_query |= Q(**{field: val})
                except json.JSONDecodeError:
                    return Response(data={"error": "Invalid JSON format for skills"}, status=status.HTTP_400_BAD_REQUEST)
            
            if parameter in ['city' , 'state' , 'country' , 'gender'] :
                field = f"{filter_match['model_field']}__{filter_match['lookup']}"
                query &= Q(**{field: value})
        
        query &= or_query
        print(query)
        return resumes.filter(query)
    
    

class FilterEmployerMixin(LocationFilterMixin , GenderFilterMixin  , CreationTimeFilterMixin) :
    
    def filter_employer(self) :
        
        employer_filter_allow_list = {
            **self.location_filter_allow_list,
            **self.gender_filter_allow_list,
            **self.creation_time_filter_allow_list,
            "title" : {"model_field" : "title" , "lookup" : "icontains"},
            "address" : {"model_field" : "address" , "lookup": "icontains"},
            "id_number" : {"model_field" : "id_number" , "lookup" : "exact"},
            "postal_code" : {"model_field" : "postal_code" , "lookup" : "exact"}
        }
        
        employer = Employer.objects.all()
        query = Q()
        parameters = self.request.query_params
        
        for parameter , value in parameters.items() :
            filter_match = employer_filter_allow_list.get(parameter)
            if not filter_match :
                return Response(data={"error" : f"{parameter} is not valid"})
            
            if parameter in ['title' , 'address' , 'id_number' , 'postal_code'] :
                model_field = filter_match['model_field'] 
                lookup = filter_match['lookup']
                query &= Q(**{f"{model_field}__{lookup}": value})
                 
            if parameter in self.location_filter_allow_list :                 
                query &= self.filter_location(parameter , value)
   
            if parameter in self.gender_filter_allow_list :      
                query &= self.filter_gender(parameter , value)
                
            if parameter in self.creation_time_filter_allow_list :
                query &= self.filter_creation_time(parameter , value)

        return employer.filter(query)
        
        
class FilterJobOpportunityMixin(LocationFilterMixin , GenderFilterMixin , CreationTimeFilterMixin) :
        def filter_job_opportunity(self , job_offers) :
        
            job_opportunity_filter_allow_list = {
                **self.location_filter_allow_list,
                **self.gender_filter_allow_list,
                **self.creation_time_filter_allow_list,
                "active" : {"model_field" : "active" , "lookup" : "exact"},
                "title" : {"model_field" : "title" , "lookup" : "icontains"},
                "status" : {"model_field" : "status" , "lookup" : "icontains"}
            }
            
            
            query = Q()
            # job_offers = JobOpportunity.objects.all()
            parameters = self.request.query_params
            
            for parameter,value in parameters.items() :
                filter_match = job_opportunity_filter_allow_list.get(parameter)
                if not filter_match :
                    return Response(data={"error" : f"{parameter} is not valid"} , status=status.HTTP_400_BAD_REQUEST)
                
                model_field = filter_match['model_field']
                lookup = filter_match['lookup']      
                      
                if parameter in ['active' , 'status' , 'title'] :
                    if parameter == 'active' :
                        value = value.title()
                    query &= Q(**{f"{model_field}__{lookup}" : value})

                if parameter in self.gender_filter_allow_list :
                    query &= self.filter_gender(parameter , value)
                    
                if parameter in self.location_filter_allow_list :
                    query &= self.filter_location(parameter , value)
                    
                if parameter in self.creation_time_filter_allow_list :
                    query &= self.filter_creation_time(parameter , value)
            
            return job_offers.filter(query)