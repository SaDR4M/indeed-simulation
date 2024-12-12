from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response


# local imports
from common.mixins import CreationTimeFilterMixin






class FilterPackageMixin(CreationTimeFilterMixin) :
    
    package_filter_allow_list = {
            **CreationTimeFilterMixin.creation_time_filter_allow_list,
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
    
    pruchase_package_filter_allow_list = {
            **CreationTimeFilterMixin.creation_time_filter_allow_list,
            "price" : {"model_field" : "package__price" , "lookup" : "exact"},
            "min_price" : {"model_field" : "package__price" , "lookup" : "gte"},
            "max_price" : {"model_field" : "package__price" , "lookup" : "lte"},
            "count" : {"model_field" : "package__count" , "lookup" : "exact"},
            "min_count" : {"model_field" : "package__count" , "lookup" : "gte"},
            "max_count" : {"model_field" : "package__count" , "lookup" : "lte"},
            "priority" : {"model_field" : "package__priority" , "lookup" : "exact"},
            "type" : {"model_field" : "type" , "package__lookup" : "exact"},
            "remaining" : {"model_field" : "remaining" , "lookup" : "exact"},
            "min_remaining" : {"model_field" : "remaining" , "lookup" : "gte"},
            "max_remaining" : {"model_field" : "remaining" , "lookup" : "lte"},
            # purchased package specific allow list
            "bought_at " : {"model_field" : "bought_at" , "lookup" : "exact"},
            "min_bought_at " : {"model_field" : "bought_at" , "lookup" : "gte"},
            "max_bought_at " : {"model_field" : "bought_at" , "lookup" : "lte"},
            "active" : {"model_field" : "active" , "lookup" : "exact"},
            "deleted_at" : {"model_field" : "package__deleted_at__date" , "lookup" : "exact"},
            "min_deleted_at" : {"model_field" : "package__deleted_at__date" , "lookup" : "gte"},
            "max_deleted_at" : {"model_field" : "package__deleted_at__date" , "lookup" : "lte"},
         }
    

    
    
        
    def filter_package(self , packages , package_type) : 
        
        query = Q()
        parameters = self.request.query_params
        
        for parameter,value in parameters.items() :
            
            if package_type == "package" : 
                field_match = self.package_filter_allow_list.get(parameter)
            if package_type == "purchased_package" : 
                field_match = self.pruchase_package_filter_allow_list.get(parameter)
                
            if not field_match :
                return Response(data={"error" : f"{parameter} is not valid"} , status=status.HTTP_400_BAD_REQUEST)        
            
            field = field_match['model_field']
            lookup = field_match['lookup']

            if parameter == 'active' : 
                query &= Q(**{f"{field}__{lookup}" : value.title()})
        
            else :
                query &= Q(**{f"{field}__{lookup}" : value})
 
        return packages.filter(query)