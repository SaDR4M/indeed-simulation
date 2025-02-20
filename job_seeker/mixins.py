# third party imports
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Q
# local imports
from core.mixins import GenderFilterMixin , LocationFilterMixin , CreationTimeFilterMixin
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
    


class FilterTestMixin(CreationTimeFilterMixin) :
    
    test_filter_allow_list = {
        **CreationTimeFilterMixin.creation_time_filter_allow_list,
        "title" : {"model_field" : "title" , "lookup" : "icontains"},
        "kind" : {"model_field" : "kind" , "lookup"  : "exact"},
        # "publish" : {"model_field" : "publish" , "lookup" : "exact"},
        # "active" : {"model_field" : "active" , "lookup" : "exact"}
        "count" : {"model_field" : "count" , "lookup" : "exact"},
        "min_count" : {"model_field" : "count" , "lookup"  : "gte"},
        "max_count" : {"model_field" : "count" , "lookup" : "lte"},
        "deleted_at" : {"model_field" : "deleted_at" , "lookup" : "exact"},
        "min_deleted_at" : {"model_field" : "deleted_at" , "lookup" : "gte"},
        "max_deleted_at" : {"model_field" : "deleted_at" , "lookup" : "lte"}
    }
    
    
    def filter_test(self , tests) :
        
        parameters = self.request.query_params
        query = Q()
        or_query = Q()
        
        
        for parameter,value in parameters.items():
            filter_match = self.test_filter_allow_list.get(parameter)
            if not filter_match :
                return Response(data={"error" : f"{parameter} is not valid"} , status=status.HTTP_400_BAD_REQUEST)
            
            # later if the kind have more fields
            
            field = filter_match['model_field']
            lookup = filter_match['lookup']
            
            if parameter == "kind" :
                values = value.split(',')
                for value in values :
                    or_query |= Q(**{f"{field}__{lookup}" : value})
            else :
                query &= Q(**{f"{field}__{lookup}" : value})
             
        query &= or_query     
           
        return tests.filter(query)
    
    
class FilterQuestionMixin(CreationTimeFilterMixin) :
    question_filter_allow_list = {
        **CreationTimeFilterMixin.creation_time_filter_allow_list,
        "question" : {"model_field" : "question" , "lookup" : "icontains"},
        "answer" : {"model_field" : "answer" , "lookup" : "icontains"},
        "score" : {"model_field" : "score" , "lookup" : "exact"},
        "min_score" : {"model_field" : "score" , "lookup" : "gte"},
        "max_score" : {"model_field" : "score" , "lookup" : "lte"},
        # "active" : {"model_field" : "active" , "lookup" : "exact"}
        "deleted_at" : {"model_field" : "deleted_at" , "lookup" : "exact"},
        "min_deleted_at" : {"model_field" : "deleted_at" , "lookup" : "gte"},
        "max_deleted_at" : {"model_field" : "deleted_at" , "lookup" : "lte"}
    }
    
    
    def filter_question(self , questions) :
        
        parameters = self.request.query_params
        query = Q()
        
        for parameter,value in parameters.items() :
            filter_match = self.question_filter_allow_list.get(parameter)
            if not filter_match :
                return Response(data={"error" : f"{parameter} is not valid"})
            field = filter_match['model_field']
            lookup = filter_match['lookup']
            
            query &= Q(**{f"{field}__{lookup}" : value})
                        
        return questions.filter(query)