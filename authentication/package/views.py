from django.shortcuts import render
import datetime
# third party imports
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from guardian.shortcuts import assign_perm
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
# local imports
from employer.models import Employer
from .serializers import PackageSerializer , PurchasePackageSerializer , GetPackageSerializer , GetPurchasedPackageSerializer
from .models import Package , PurchasedPackage
from payment.models import Payment
from employer.utils import employer_exists
from .mixins import FilterPackageMixin
from rest_framework.pagination import LimitOffsetPagination
# Create your views here.

# only admins can create package for job offers
# admin and employers can create package to view resume
class CreatePackage(APIView) :
    
    @swagger_auto_schema(
        operation_summary="create payment",
        operation_description="create payment",
        responses={
            200 : PackageSerializer,
            400 : "invalid parameters",
            404 : "job seeker was not found"
        }
    )
    def get(self , request) :
        user = request.user
        if not user.is_superuser :
            return Response(data={"detail" : "user does not have permission to do this action"} , status=status.HTTP_403_FORBIDDEN)
        packages = Package.objects.filter(user=user)
        if not packages.exists() :
            return Response(data={"detail" : "there is no package for this admin"} , status=status.HTTP_404_NOT_FOUND)
        serializer = PackageSerializer(packages , many=True)
        return Response(data={"detail" : serializer.data} , status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="create package",
        operation_description="admins create package",
        request_body=PackageSerializer,
        responses={
            200 : "package created succesfsully",
            400 : "invalid parameters",
            404 : "job seeker was not found"
        }
    ) 
    def post(self , request) :
        user = request.user
        if not user.is_superuser :
            return Response(data={"detail" : "user does not have permission to do this action"} ,status=status.HTTP_403_FORBIDDEN)
        serializer = PackageSerializer(data=request.data)
        if serializer.is_valid() :
            count = serializer.validated_data['count']
            package_type  = serializer.validated_data['type']
            price = serializer.validated_data['price']

            if price <= 0 :
                return Response(data={"error" : "price must be more than 0 "} , status=status.HTTP_400_BAD_REQUEST) 
            
            if count <= 0 :
                return Response(data={"error" : "count must be more than 1"} , status=status.HTTP_400_BAD_REQUEST)
            
            
            if package_type == "resume" :
                priority = "normal"
            else :
                priority = serializer.validated_data['priority']
            package = Package.objects.filter(type=package_type, priority=priority, count=count, active=True).count()
            if package >= 1:
                return Response(data={"detail" : "with this count you can only have on active package , deactive the other packages to register this package"} , status=status.HTTP_400_BAD_REQUEST)
            serializer.save(user=user)
            return Response(data={"detail" : "Package created successfully"} , status=status.HTTP_201_CREATED)
        return Response(data={"errors" : serializer.errors } , status=status.HTTP_400_BAD_REQUEST)
    
    
    @swagger_auto_schema(
        operation_summary="delete package",
        operation_description="admins virtual delete the package if there is a package",
        responses={
            200 : "package deeleted successfully",
            400 : "invalid parameters",
            404 : "job seeker was not found"
        }
    )
    def delete(self , request) :
        user = request.user
        package_id = request.data.get('package_id')
        if not package_id :
            return Response(data={"detail" : "package_id must be entered"} , status=status.HTTP_400_BAD_REQUEST)
        
        if not user.is_superuser :
            return Response(data={"detail" : "user does not have permission to do this action"} , status=status.HTTP_403_FORBIDDEN)
        package = Package.objects.filter(pk=int(package_id))
        
        if not package.exists() :
            return Response(data={"detail" : "package does not exist"} , status=status.HTTP_404_NOT_FOUND)
        
        package.update(active=False , deleted_at = datetime.datetime.now())
        return Response(data={"detail" : "package deleted successfully"} , status=status.HTTP_200_OK)
        
           
        
class PurchasePackage(APIView , FilterPackageMixin) :
    @swagger_auto_schema(
        operation_summary="list of purchased pacakges",
        operation_description="show the list of the purchase pacakges if the employer exists and bought at least one pacakge",
        responses={
            200 : PurchasePackageSerializer,
            400 : "invalid parameters",
            404 : "job seeker was not found"
        }
    )
    def get(self , request) :
        user = request.user
        
        employer = employer_exists(user)
        if not employer:
            return Response(data={"detail" : "employer does not exists"} , status=status.HTTP_400_BAD_REQUEST)

        
        purchased = PurchasedPackage.objects.filter(employer = employer)
        if not purchased.exists() :
            return Response(data={"detail" : "there is purchased pacakge for this user"})
        # filter the data
        filtered_data = self.filter_package(purchased , "purchased_package")
        if isinstance(filtered_data , Response) :
            return filtered_data
        
        for data in filtered_data :
            if not user.has_perm("view_purchasedpackage" , data) :
                return Response(data={"error" : "user does not have permission to do this action"} , status=status.HTTP_403_FORBIDDEN)
        
        # paginate the data
        paginator = LimitOffsetPagination()
        paginator.paginate_queryset(filtered_data,request)
        
        
        
        data = []
        for purchased in filtered_data :
            # serialize the purchased package
            purchased_package_serializer = GetPurchasedPackageSerializer(purchased).data
            # serialize the package then add it to purchased package
            package_serializer = GetPackageSerializer(purchased.package).data
            purchased_package_serializer['package'] = package_serializer
            data.append(purchased_package_serializer)
        
        return Response(data={"success" : True , "data" : data} , status=status.HTTP_200_OK)
    
    
    
    @swagger_auto_schema(
        operation_summary="create payment",
        operation_description="purchase package if the payment is completed",
        request_body=PurchasePackageSerializer,
        responses={
            200 : "purchase was successfull",
            400 : "invalid parameters",
            404 : "job seeker was not found"
        }
    )
    def post(self , request) :
        user = request.user
        employer = employer_exists(user)
        if not employer:
            return Response(data={"detail" : "employer does not exists"} , status=status.HTTP_400_BAD_REQUEST)
        serializer = PurchasePackageSerializer(data=request.data , context = {"request" : request})
        if serializer.is_valid() :
            data = serializer.validated_data
            payment = data['payment']
            package = data['package']
            # not acitve packages can not be bought        
            if package.active == False :
                return Response(data={"detail" : "Package is not available"} , status=status.HTTP_404_NOT_FOUND)
            # only completed payments can buy packages
            if payment.status == "completed" :
                purchased = serializer.save(employer=employer , payment=payment , package=package)
                return Response(data={"detail" : "Purchase was successfull"} , status=status.HTTP_201_CREATED)
            return Response(data={"detail" : f" failed ,  purchase status : {payment.status}"} , status=status.HTTP_400_BAD_REQUEST)
        return Response(data={"detail" : serializer.errors } , status=status.HTTP_400_BAD_REQUEST)


# TODO ADD THIS TO THE ADMIN APP

class AllPackage(APIView , FilterPackageMixin) :
    @swagger_auto_schema(
    operation_summary="all packages",
    operation_description="get all packages with filtering that . filtering option are specified in the query params document",
    manual_parameters=[
        openapi.Parameter(name="price" , in_=openapi.IN_QUERY , type=openapi.TYPE_NUMBER , description="get the packages with this EXACT price (for having range price you must define max and min price together)"),
        openapi.Parameter(name="min_price" , in_=openapi.IN_QUERY , type=openapi.TYPE_NUMBER , description="get the packages with MIN price (lte)"),
        openapi.Parameter(name="max_price" , in_=openapi.IN_QUERY , type=openapi.TYPE_NUMBER , description="get the packages with MAX price (gte)"),
        openapi.Parameter(name="active" , in_=openapi.IN_QUERY , type=openapi.TYPE_BOOLEAN , description="get the packages with EXACT type . options are True , False"),
        openapi.Parameter(name="count" , in_=openapi.IN_QUERY , type=openapi.TYPE_INTEGER , description="get the packages with EXACT count"),
        openapi.Parameter(name="type" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the packages with EXACT type. options are : 'offer' , 'resume' "),
        openapi.Parameter(name="priority" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the packages with EXACT priority. options are : 'normal' , 'urgent' "),
        openapi.Parameter(name="created_at" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING, description="get the packages with this EXACT created date time (for having range date time you must define max and min created date time together)"),
        openapi.Parameter(name="min_created_at" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the packages with MIN created date time (lte)"),
        openapi.Parameter(name="max_created_at" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the packages with MAX created date time  (gte)"),
        openapi.Parameter(name="deleted_at" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING, description="get the packages with this EXACT deleted date time (for having range date time you must define max and min deleted date time together)"),
        openapi.Parameter(name="min_deleted_at" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the packages with MIN deleted date time (lte)"),
        openapi.Parameter(name="max_deleted_at" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the packages with MAX deleted date time  (gte)"),
    ],
    responses={
            200 : GetPackageSerializer,
            400 : "invalid parameters",
            404 : "employer/offer was not found",
        },
    security=[{"Bearer" : []}]
    )
    def get(self , request) :
        user = request.user 
        if not user.is_superuser :
            return Response(data={"error" : "user does not have permission to do this action"} , status=status.HTTP_403_FORBIDDEN)
        
        packages = Package.objects.all()
        filtered_package = self.filter_package(packages , "package")
        if isinstance(filtered_package , Response) :
            return filtered_package
        
        # paginate the data
        paginator = LimitOffsetPagination()
        paginator.paginate_queryset(filtered_package , request)
        
        serializer = GetPackageSerializer(filtered_package , many=True)
        return Response(data={"data" : serializer.data} , status=status.HTTP_200_OK)