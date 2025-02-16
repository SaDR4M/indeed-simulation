# from rest_framework import status
# from rest_framework.response import Response


# def model_field_lookup(allow_list , parameter) :
#     filter_match = allow_list.get(parameter)
#     if filter_match :
#         model_field = filter_match['model_filed']
#         lookup = filter_match['lookup']
#         return [model_field , lookup]
#     return Response(data={"error" : "error with the list of allowing filter"} , status=status.HTTP_400_BAD_REQUEST)