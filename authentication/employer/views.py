from django.shortcuts import render

# third party imports
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# local imports
from .models import Employer , JobOpportunity
# Create your views here.

class EmployerRegister(APIView) :
    
    def post(self , request) :
        print(request.user)
        company_name = request.data.get('company_name')
        return Response(data={"test"} , status=status.HTTP_200_OK)
        