# third party imports
from django.db import models 
from django.db.models import Q
from account.models import Cities , States , Countries
from rest_framework import status
from rest_framework.response import Response

class GenderFilterMixin(models.Model) :
    class GenderChoices(models.TextChoices) :
        MALE = "male"
        FEMALE = "female"
    
    gender = models.CharField(choices=GenderChoices.choices , null=False , blank=False)
    
    class Meta:
        abstract = True  
        

class LocationFilterMixin(models.Model) :
    
    def filter_location(self) :
        print('test_lo')
        
        location_allow_list_filter = {
            "city" : {"model_field" : "city__name" , "lookup" : "iexact"},
            "state" : {"model_field" : "state__name" , "lookup" : "iexact"},
            "country" : {"model_field" : "country__name" , "lookup" : "iexact"}            
        }        

        query = Q()
        or_query = Q()
        parameters = self.request.query_params
        for parameter,value in parameters.items() :
            filter_match = location_allow_list_filter.get(parameter) 
            if not filter_match :
                return Response(data={"error" : f"{parameter} is not valid parameter"} , status=status.HTTP_400_BAD_REQUEST)
            
            field = filter_match['model_field']
            look_up = filter_match['lookup']
            
            if isinstance(value , str) :
                query &= Q(**{f"{field}__{look_up}" : value})
                
            if isinstance(value , list) :
                for data in value :
                    query |= Q(**{f"{field}__{look_up}" : data})
        
        query &= or_query
        print(query)
        return query