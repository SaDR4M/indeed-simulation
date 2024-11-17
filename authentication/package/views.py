from django.shortcuts import render
import datetime
# third party imports
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from guardian.shortcuts import assign_perm
# local imports
from employer.models import Employer
from .serializers import PackageSerializer , PurchasePackageSerializer
from .models import Package , PurchasedPackage
from payment.models import Payment
# Create your views here.

# only admins can create package for job offers
# admin and employers can create package to view resume
class CreatePackage(APIView) :
    
    def get(self , request) :
        user = request.user
        if not user.is_staff :
            return Response(data={"detail" : "user does not have permission to do this action"} , status=status.HTTP_403_FORBIDDEN)
        packages = Package.objects.filter(user=user)
        if not packages.exists() :
            return Response(data={"detail" : "there is no package for this admin"} , status=status.HTTP_404_NOT_FOUND)
        serializer = PackageSerializer(packages , many=True)
        return Response(data={"detail" : serializer.data} , status=status.HTTP_200_OK)
        return Response(data={"detail" : serializer.errors} , status=status.HTTP_400_BAD_REQUEST)

        
    def post(self , request) :
        user = request.user
        if not user.is_staff :
            return Response(data={"detail" : "user does not have permission to do this action"} ,status=status.HTTP_403_FORBIDDEN)
        serializer = PackageSerializer(data=request.data)
        if serializer.is_valid() :
            serializer.save(user=user)
            return Response(data={"detail" : "Package created successfully"} , status=status.HTTP_201_CREATED)
        return Response(data={"errors" : serializer.errors } , status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self , request) :
        user = request.user
        package_id = int(request.data.get('package_id'))
        if not package_id :
            return Response(data={"detail" : "package id must be entered"} , status=status.HTTP_400_BAD_REQUEST)
        
        if not user.is_staff :
            return Response(data={"detail" : "user does not have permission to do this action"} , status=status.HTTP_403_FORBIDDEN)
        package = Package.objects.filter(pk=package_id)
        
        if not package.exists() :
            return Response(data={"detail" : "package does not exist"} , status=status.HTTP_404_NOT_FOUND)
        
        package.update(active=False , deleted_at = datetime.datetime.now().strftime('%Y-%m-%d , %H:%M:%S'))
        return Response(data={"detail" : "package deleted successfully"} , status=status.HTTP_200_OK)
        
           
        
class PurchasePackage(APIView) :
    
    def post(self , request) :
        user = request.user
        print(user)
        try :
           employer = Employer.objects.get(user=user)
        except Employer.DoesNotExist :
            return Response(data={"detail" : "employer does not exists"} , status=status.HTTP_400_BAD_REQUEST)
        serializer = PurchasePackageSerializer(data=request.data , context = {"request" : request})
        if serializer.is_valid() :
            data = serializer.validated_data
            # data[user] = user
            payment = data['payment']
            package = data['package']
            payment_status = payment.status
            if payment_status == "completed" :
                serializer.save(employer=employer , payment=payment , package=package)
                return Response(data={"detail" : "Purchase was successfull"} , status=status.HTTP_201_CREATED)
            return Response(data={"detail" : f" faild ,  purchase status : {payment_status}"} , status=status.HTTP_400_BAD_REQUEST)
        return Response(data={"detail" : serializer.errors } , status=status.HTTP_400_BAD_REQUEST)


