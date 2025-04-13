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
        operation_summary="purchase package",
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
            # payment = data['payment']
            package = data['package']
            # not acitve packages can not be bought        
            if package.active == False :
                return Response(data={"detail" : "Package is not available"} , status=status.HTTP_404_NOT_FOUND)
            # NOTE for bypassing the payment
            else :
                serializer.save(employer=employer , package=package)
                return Response(data={"detail" : "Purchase was successfull"} , status=status.HTTP_201_CREATED)
            # only completed payments can buy packages
            # if payment.status == "completed" :
            #     purchased = serializer.save(employer=employer , payment=payment , package=package)
            #    return Response(data={"detail" : "Purchase was successfull"} , status=status.HTTP_201_CREATED)
            # return Response(data={"detail" : f" failed ,  purchase status : {payment.status}"} , status=status.HTTP_400_BAD_REQUEST)
        return Response(data={"detail" : serializer.errors } , status=status.HTTP_400_BAD_REQUEST)

