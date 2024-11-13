from django.shortcuts import render

# third party imports
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from . import serializers
# local imports
from .serializers import EmployerSerializer , JobOpportunitySerializer
from .models import Employer, JobOpportunity


# Create your views here.

class EmployerRegister(APIView) :
    def get(self , request):
        user = request.user
        employer = Employer.objects.filter(user=user)
        if not employer.exists():
            return Response(data={"detail" : "there is no employer assign to this user"})

        serializer = EmployerSerializer(employer)
        return Response(data={"detail" : serializer.data} , status=status.HTTP_200_OK)


    def post(self , request) :
        # check if the employer exist or not
        if Employer.objects.filter(user=request.user).exists() :
            return Response(data={"detail" : "Employer exists"})
        serializer = EmployerSerializer(data=request.data)
        if serializer.is_valid() :
            data = serializer.validated_data
            # adding the user to the validated data
            data['user'] = request.user
            serializer.save()
            return Response(data={"detail" : "Employer registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(data={"errors" : serializer.errors} , status=status.HTTP_200_OK)

class JobOffer(APIView) :
    def get(self , request):
        user = request.user
        # check for employer exist
        employer = Employer.objects.filter(user=user)
        if not employer.exists():
            return Response(data={"detail" : "employer does not exists"} , status=status.HTTP_404_NOT_FOUND)
        # check for offers to exist
        job_opportunities = JobOpportunity.objects.filter(employer=employer)
        if not job_opportunities.exists():
            return Response(data={"detail" : "there is no opportunity for this employer"})

        serializer = JobOpportunitySerializer(job_opportunities , many=True)
        return Response(data={"detail" : serializer.data } , status=status.HTTP_200_OK)

    def post(self , request) :
        user = request.user
        employer = Employer.objects.filter(user=user)

        # check for employer to exist
        if not employer.exists():
            return Response(data={"detail" : "employer does not exists"} , status=status.HTTP_404_NOT_FOUND)

        serializer = JobOpportunitySerializer(data=request.data)
        if serializer.is_valid() :
            data = serializer.validated_data
            data['employer'] = employer
            serializer.save()
            return Response(data={"detail" : "Job Opportunity created successfully"} , status=status.HTTP_201_CREATED)
        return Response(data={"errors" : serializer.errors} , status=status.HTTP_200_OK)

    
class AllJobOffers(APIView) :
    def get(self , request):
        job_opportunities = JobOpportunity.objects.all()
        serializer = JobOpportunitySerializer(job_opportunities , many=True)
        return Response(data={"detail" : serializer.data } , status=status.HTTP_200_OK)