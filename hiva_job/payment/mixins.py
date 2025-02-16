    
# third party imports
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Q



# local imports




class FitlerPaymentMixin:
    
    
    payment_filter_allow_list = {
        "authority" : {"model_field" : "authority" , "lookup" : "icontains"},
        "checkout_at" : {"model_field" : "checkout_at" , "lookup" : "exact"},
        "amount" : {"model_field" : "min_amount" , "lookup" : "exact"},      
        "min_amount" : {"model_field" : "min_amount" , "lookup" : "gte"},
        "max_amount" : {"model_field" : "min_amount" , "lookup" : "lte"},
        "min_checkout_at" : {"model_field" : "checkout_at" , "lookup" : "gte"},
        "max_checkout_at" : {"model_field" : "checkout_at" , "lookup" : "lte"},
        "payment_id" : {"model_field" : "payment_id" , "lookup" : "icontains"},
        "status" : {"model_field" : "status" , "lookup" : "exact"},
    }
    
    
    
    def filter_payment(self , payments) :
        
        query = Q()
        parameters = self.request.query_params
        
        
        for parameter,value in parameters.items() :
            filter_match = self.payment_filter_allow_list.get(parameter)
            if not filter_match :
                return Response(data={"error" : f"{parameter} is not valid"}  , status=status.HTTP_400_BAD_REQUEST)
            
            field = filter_match['model_field']
            lookup = filter_match['lookup']
            
            
            query &= Q(**{f"{field}__{lookup}" : value})
            
        return payments.filter(query)