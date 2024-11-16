from django.shortcuts import render
# third party imports
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from guardian.shortcuts import assign_perm
# local imports
from employer.models import Employer
from .serializers import PackageSerializer , PurchasePackageSerializer
# Create your views here.

# only admins can create package for job offers
# admin and employers can create package to view resume
class CreatePackage(APIView) :
    
    def get(self , request) :
        pass
    
    def post(self , request) :
        user = request.user
        if not user.is_staff :
            return Response(data={"detail" : "user does not have permission to do this action"} ,status=status.HTTP_403_FORBIDDEN)
        serializer = PackageSerializer(data=request.data)
        if serializer.is_valid() :
            data = serializer.validated_data
            serializer.save()
            return Response(data={"detail" : "Package created successfully"} , status=status.HTTP_201_CREATED)
        return Response(data={"errors" : serializer.errors } , status=status.HTTP_400_BAD_REQUEST)
        
        
class PurchasePackage(APIView) :
    def post(self , request) :
        user = request.user
        try :
           employer = Employer.objects.get(user=user)
        except Employer.DoesNotExist :
            return Response(data={"detail" : "employer does not exists"} , status=status.HTTP_400_BAD_REQUEST)
        serializer = PurchasePackageSerializer(data=request.data)
        if serializer.is_valid() :
            data = serializer.validated_data
            data['employer'] = employer
            print(employer.user)
            print(data)
            serializer.save()
            return Response(data={"detail" : "Purchase was successfull"} , status=status.HTTP_201_CREATED)
        return Response(data={"detail" : serializer.errors } , status=status.HTTP_400_BAD_REQUEST)


