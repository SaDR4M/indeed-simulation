import json
# third party imports
from django.db import models 
from django.db.models import Q
from account.models import Cities , States , Countries
from rest_framework import status
from rest_framework.response import Response
# local imports


# TODO  refactor the MODEL_FIELD and LOOKUP to the utils
# import utils

class GenderMixin(models.Model) :
    class GenderChoices(models.TextChoices) :
        MALE = "male"
        FEMALE = "female"
    
    gender = models.CharField(choices=GenderChoices.choices , null=False , blank=False)
    
    class Meta:
        abstract = True  
        

class LocationFilterMixin(models.Model) :
    
    def value_validations(self) :
        pass
    
    
    
    
    location_filter_allow_list = {
            "city" : {"model_field" : "city__name" , "lookup" : "iexact"},
            "state" : {"model_field" : "state__name" , "lookup" : "iexact"},
            "country" : {"model_field" : "country__name" , "lookup" : "iexact"}            
    }   
    
    def filter_location(self , parameter , value) :
            
        query = Q()
        or_query = Q()
        filter_match = self.location_filter_allow_list.get(parameter) 
        if filter_match :
            field = filter_match['model_field']
            look_up = filter_match['lookup']

            if "," in value :
                values = value.split(",")
                for value in values :
                    query |= Q(**{f"{field}__{look_up}" : value.strip()})
            else :
                query &= Q(**{f"{field}__{look_up}" : value.strip()})
            
                
            query &= or_query
            return query
        
    
    
class GenderFilterMixin:
    
    gender_filter_allow_list = {
            "gender" : {"model_field" : "gender" , "lookup" : "exact"}
    }
    
    def filter_gender(self , parameter , value) :
        query = Q()
    
        filter_match = self.gender_filter_allow_list.get(parameter)
        if filter_match :
            field = filter_match['model_field']
            lookup = filter_match['lookup']
                    
            query &= Q(**{f"{field}__{lookup}" : value})
            
            return query
                
                
                
class CreationTimeFilterMixin:
    creation_time_filter_allow_list = {
        "created_at" : {"model_field" : "created_at" , "lookup" : "exact"},
        "created_min" : {"model_field" : "created_at" , "lookup" : "gte"},
        "created_max" : {"model_field" : "created_at" , "lookup" : "lte"}
    }
    
    
    def filter_creation_time(self , parameter , value) :
        query = Q()
        filter_match = self.creation_time_filter_allow_list.get(parameter)
        if filter_match :
            model_field = filter_match['model_field']
            lookup = filter_match['lookup']
            
            query &= Q(**{f"{model_field}__date__{lookup}" : value})
            
            return query