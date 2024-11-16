from django.shortcuts import render

# third party imports
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from guardian.shortcuts import assign_perm
from account import serializer

# local imports
from .serializers import EmployerSerializer , JobOpportunitySerializer
from .models import Employer, JobOpportunity
from job_seeker.utils import assign_base_permissions
from . import serializers


# Create your views here.

class EmployerRegister(APIView) :
    def get(self , request):
        user = request.user
        employer = Employer.objects.filter(user=user)
        if not employer.exists():
            return Response(data={"detail" : "there is no employer assign to this user"})
        # check for the user permission
        if not user.has_perm('view_employer' , employer[0]) :
            return Response(data={"detail" : "user does not have permission to view this"} , status=status.HTTP_403_FORBIDDEN)
        serializer = EmployerSerializer(employer[0])
        return Response(data={"detail" : serializer.data} , status=status.HTTP_200_OK)


    def post(self , request) :
        # check if the employer exist or not
        user = request.user
        employer = Employer.objects.filter(user=request.user)
        if employer.exists() :
            return Response(data={"detail" : "Employer exists"} , status=status.HTTP_400_BAD_REQUEST)
        serializer = EmployerSerializer(data=request.data)
        if serializer.is_valid() :
            data = serializer.validated_data
            # adding the user to the validated data
            data["user"] = user
            employer = serializer.save()
            # assign the permission to the user
            assign_perm('view_employer' , user , employer)
            assign_perm('delete_employer' , user , employer)
            return Response(data={"detail" : "Employer registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(data={"errors" : serializer.errors} , status=status.HTTP_200_OK)

    
    def patch(self , request) :
        user = request.user
        try :
            employer = Employer.objects.get(user=user)
        except Employer.DoesNotExist:
            return Response(data={"detail" : "employer does not exists"} , status=status.HTTP_404_NOT_FOUND)
        
        if not user.has_perm('change_employer' , employer) :
            return Response(data={"detail" : "user does not have permission to do this"} , status=status.HTTP_403_FORBIDDEN)
        
        serializer = EmployerSerializer(employer , data=request.data , partial=True)
        if serializer.is_valid() :
            data = serializer.validated_data
            data['user'] = user
            serializer.save()
            return Response(data={"employer updated successfully"} , status=status.HTTP_200_OK)
            
        return Response(data={serializer.erros} , status=status.HTTP_400_BAD_REQUEST) 

        

    
    
class JobOffer(APIView) :
    def get(self , request):
        user = request.user
        # check for employer exist
        employer = Employer.objects.filter(user=user)
        if not employer.exists():
            return Response(data={"detail" : "employer does not exists"} , status=status.HTTP_404_NOT_FOUND)
        # check for offers to exist
        job_opportunities = JobOpportunity.objects.filter(employer=employer[0])
        if not job_opportunities.exists():
            return Response(data={"detail" : "there is no opportunity for this employer"})
        if not user.has_perm('view_jobopportunity' , job_opportunities[0]) :
            return Response(data={"detail" : "user does not have permissions for this action"} , status=status.HTTP_403_FORBIDDEN)
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
            data['employer'] = employer[0]
            offer = serializer.save()
            assign_perm("view_jobopportunity" , user , offer)
            assign_perm("change_jobopportunity" , user , offer)
            return Response(data={"detail" : "Job Opportunity created successfully"} , status=status.HTTP_201_CREATED)
        return Response(data={"errors" : serializer.errors} , status=status.HTTP_200_OK)

    def patch(self , request) :
        user = request.user
        offer_id = int(request.data['offer_id'])
        if not offer_id :
            return Response(data={"detail" : "enter the offer id"} , status=status.HTTP_400_BAD_REQUEST)
        try :
            employer = Employer.objects.get(user=user)
        except Employer.DoesNotExist :
            return Response(data={"detail" : "employer does not exists"} , status=status.HTTP_404_NOT_FOUND)
        try :
            job_opportunity = JobOpportunity.objects.get(pk=offer_id)
        except JobOpportunity.DoesNotExist :
            return Response(data={"detail" : "there is no job offers assign to this user"} , status=status.HTTP_404_NOT_FOUND)
        # if not user.has_perm('change_jobopportunity' , employer) :
        #     return Response(data={"detail" : "user does not have permission to do this action" } , status=status.HTTP_403_FORBIDDEN)
        serializer = JobOpportunitySerializer(job_opportunity , data=request.data , partial=True)
        if serializer.is_valid() :
            data = serializer.validated_data
            data['employer'] = employer
            serializer.save()
            return Response(data={"detail" : "job offer updated succesfully"} , status=status.HTTP_200_OK)
        return Response(data={"errors" : serializer.errors} , status=status.HTTP_400_BAD_REQUEST)

    def delete(self , request):
        user = request.user
        offer_id = request.data.get('offer_id')
        if not offer_id :
            return Response(data={"detail" : "enter the offer id"} , status=status.HTTP_400_BAD_REQUEST)
        try:
            employer = Employer.objects.get(user=user)
        except Employer.DoesNotExist :
            return Response(data={"detail" : "employer does not exists"} , status=status.HTTP_404_NOT_FOUND)
        if not user.has_perm("delete_jobopportunity") :
            return Response(data={"detail" : "employer does not have permission to do this action"} , status=status.HTTP_403_FORBIDDEN)
        JobOpportunity.objects.get(pk=offer_id).delete()
        return Response(data={"detail" : "deleted successfully" } , status=status.HTTP_200_OK)


class AllJobOffers(APIView) :
    def get(self , request):
        job_opportunities = JobOpportunity.objects.all()
        serializer = JobOpportunitySerializer(job_opportunities , many=True)
        return Response(data={"detail" : serializer.data } , status=status.HTTP_200_OK)