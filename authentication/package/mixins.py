from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response


# local imports
from common.mixins import CreationTimeFilterMixin






class FilterPackageMixin(CreationTimeFilterMixin) :
    
    
    
    def filter_package(self , packages) : 
        package_filter_allow_list = {
            **self.creation_time_filter_allow_list,
            "price" : {"model_field" : "price" , "lookup" : "exact"},
            "min_price" : {"model_field" : "price" , "lookup" : "gte"},
            "max_price" : {"model_field" : "price" , "lookup" : "lte"},
            "count" : {"model_field" : "count" , "lookup" : "exact"},
            "min_count" : {"model_field" : "count" , "lookup" : "gte"},
            "max_count" : {"model_field" : "count" , "lookup" : "lte"},
            "priority" : {"model_field" : "priority" , "lookup" : "exact"},
            "type" : {"model_field" : "type" , "lookup" : "exact"},
            "active" : {"model_field" : "active" , "lookup" : "exact"},
            "deleted_at" : {"model_field" : "deleted_at__date" , "lookup" : "exact"},
            "min_deleted_at" : {"model_field" : "deleted_at__date" , "lookup" : "gte"},
            "max_deleted_at" : {"model_field" : "deleted_at__date" , "lookup" : "lte"}
        }    
        
        query = Q()
        parameters = self.request.query_params
        
        for parameter,value in parameters.items() :
            field_match = package_filter_allow_list.get(parameter)
            if not field_match :
                return Response(data={"error" : f"{parameter} is not valid"} , status=status.HTTP_400_BAD_REQUEST)        
            
            field = field_match['model_field']
            lookup = field_match['lookup']

            if parameter == 'active' : 
                query &= Q(**{f"{field}__{lookup}" : value.title()})
        
            else :
                query &= Q(**{f"{field}__{lookup}" : value})
 
        return packages.filter(query)