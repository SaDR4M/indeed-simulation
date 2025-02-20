
# django & rest
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
# local
from package.mixins import FilterPackageMixin



class FilterOrderMixin(FilterPackageMixin):
    
    
    def filter_order(self , orders) :
        
        order_filter_allow_list = {
            "status" : {"model_field" : "status" , "lookup" : "exact"},
            "order_at" : {"model_field" : "status" , "lookup" : "exact"},
            "min_order_at" : {"model_field" : "status" , "lookup" : "gte"},
            "max_order_at" : {"model_field" : "status" , "lookup" : "lte"},
            "price" : {"model_field" : "order_items__package__price" , "lookup" : "exact"},
            "min_price" : {"model_field" : "order_items__package__price" , "lookup" : "gte"},
            "max_price" : {"model_field" : "order_items__package__price" , "lookup" : "lte"},
            "count" : {"model_field" : "order_items__package__count" , "lookup" : "exact"},
            "min_count" : {"model_field" : "order_items__package__count" , "lookup" : "gte"},
            "max_count" : {"model_field" : "order_items__package__count" , "lookup" : "lte"},
            "priority" : {"model_field" : "order_items__package__priority" , "lookup" : "exact"},
            "type" : {"model_field" : "order_items__package__type" , "lookup" : "exact"},
            "active" : {"model_field" : "order_items__package__active" , "lookup" : "exact"},
            "deleted_at" : {"model_field" : "order_items__package__deleted_at__date" , "lookup" : "exact"},
            "min_deleted_at" : {"model_field" : "order_items__package__deleted_at__date" , "lookup" : "gte"},
            "max_deleted_at" : {"model_field" : "order_items__package__deleted_at__date" , "lookup" : "lte"}
        }
        
        
        query = Q()
        parameters = self.request.query_params
        or_query = Q()
        
        for parameter,value in parameters.items() :
            filter_match = order_filter_allow_list.get(parameter)
            if not filter_match :
                return Response(data={"error" : f"{parameter} is not valid"} , status=status.HTTP_400_BAD_REQUEST)
            
            model_field = filter_match['model_field']
            lookup = filter_match['lookup']
            if "," in value : 
                values = value.split(",")
                for value in values :
                    or_query |= Q(**{f"{model_field}__{lookup}" : value})
            else :
                query &= Q(**{f"{model_field}__{lookup}" : value})
            
        query &= or_query
        print(query)
        return orders.filter(query)