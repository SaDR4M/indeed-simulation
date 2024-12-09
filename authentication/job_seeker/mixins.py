# third party imports
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Q
# local imports
from common.mixins import GenderFilterMixin , LocationFilterMixin , CreationTimeFilterMixin
from .models import JobSeeker






class JobSeekerFilterMixin(GenderFilterMixin , LocationFilterMixin  , CreationTimeFilterMixin):        
    
    
    def filter_jobseeker(self) :
        jobseeker_filter_allow_lost = {
            **self.location_filter_allow_list,
            **self.gender_filter_allow_list,
            **self.creation_time_filter_allow_list,
            "birthday" : {"model_field" : "birthday" , "lookup" : "exact"},
            "birthday_min" : {"model_field" : "birthday" , "lookup" : "gte"},
            "birthday_max" : {"model_field" : "birthday" , "lookup" : "lte"},
        }
        print(jobseeker_filter_allow_lost)
        
        parameters = self.request.query_params
        query = Q()
        jobseekers = JobSeeker.objects.all()
        
        for parameter,value in parameters.items() :
            filter_match = jobseeker_filter_allow_lost.get(parameter)
            if not filter_match :
                return Response(data={"error" : f"{parameter} is not valid"} , status=status.HTTP_400_BAD_REQUEST)
            
            if parameter in [ 'birthday' , "birthday_min" , "birthday_max" ] :
                model_field = filter_match['model_field']
                lookup = filter_match['lookup']
                query &= Q(**{f"{model_field}__{lookup}" : value})
                
            if parameter in self.location_filter_allow_list :
                query &= self.filter_location(parameter , value)
                
            if parameter in self.gender_filter_allow_list :
                query &= self.filter_gender(parameter , value)
                
            if parameter in self.creation_time_filter_allow_list :
                query &= self.filter_creation_time(parameter , value)
        
        
        return  jobseekers.filter(query)