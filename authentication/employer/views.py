import datetime
from dataclasses import dataclass


# third party imports
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK , HTTP_201_CREATED , HTTP_400_BAD_REQUEST ,HTTP_401_UNAUTHORIZED , HTTP_403_FORBIDDEN , HTTP_404_NOT_FOUND
from guardian.shortcuts import assign_perm
from account import serializer
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.db import transaction
from package.serializers import PackageSerializer
from django.utils.timezone import make_aware , make_naive
from rest_framework.pagination import LimitOffsetPagination
# local imports
from .serializers import (EmployerSerializer,
                          JobOpportunitySerializer,
                          ViewedResumeSerializer,
                          ChangeApllyStatusSerializer,
                          CartSerializer,
                          CartItemSerializer, OrderSerializer, OrderItemSerializer, ChangeInterviewEmployerScheduleSerializer , InterviewScheduleSerializer
                          )
                          
from .models import Employer, JobOpportunity, ViewedResume , EmployerCart , EmployerCartItem , EmployerOrderItem , EmployerOrder , InterviewSchedule
from job_seeker.utils import assign_base_permissions
from . import utils
from job_seeker.models import Resume , Application
from job_seeker.serializers import ApplicationSerializer, ResumeSerializer , GetResumeSerializer
from package.models import PurchasedPackage, Package
from .utils import can_create_offer, employer_exists
from celery.result import AsyncResult
from job_seeker.utils import job_seeker_exists
from .mixins import InterviewScheduleMixin , FilterResumseMixin , CountryCityIdMixin
from django.db.models import Q
from rest_framework.pagination import LimitOffsetPagination
# sms
from account.tasks import send_order_sms , send_order_email
from account.models import Message
from . import tasks
# Create your views here.

class EmployerRegister(APIView , CountryCityIdMixin) :
    @swagger_auto_schema(
    operation_summary="get employer infomartion",
    operation_description="get the employer information if the user is employer",
    responses= {
        200 : EmployerSerializer,   
        400 : "invalid parameters",
        403 : "does not have permission to get this data",
        404 : "did't found the employer"
        
    },
    security=[{"Bearer" : []}]
    )
    def get(self , request):
        user = request.user
        employer = utils.employer_exists(user)
        if not employer :
            return Response(data={"detail" : "there is no employer assign to this user"} , status=HTTP_404_NOT_FOUND)
        # check for the user permission
        if not user.has_perm('view_employer' , employer) :
            return Response(data={"detail" : "user does not have permission to view this"} , status=HTTP_403_FORBIDDEN)
        serializer = EmployerSerializer(employer)
        return Response(data={"detail" : serializer.data} , status=HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="register employer",
        operation_description="register the user if this user is not employer",
        request_body= EmployerSerializer,
        responses= {
            201 : "employer created successfully",
            400 : "invalid parameters",    
        }
    )
    def post(self , request) :
        # check if the employer exist or not
        user = request.user
        employer = Employer.objects.filter(user=request.user)

        if employer.exists() :
            return Response(data={"detail" : "Employer exists"} , status=HTTP_400_BAD_REQUEST)
        serializer = EmployerSerializer(data=request.data)
        if serializer.is_valid() :

            data = self.country_and_city_id(request)
            if isinstance(data , Response):
                return data
            city = data['city']
            country = data['country']
            state = data['state']
            # adding the user to the validated data
            employer = serializer.save(user=user , city=city , country=country , state=state)
            # assign the permission to the user
            assign_perm('view_employer' , user , employer)
            assign_perm('delete_employer' , user , employer)
            return Response(data={"detail" : "Employer registered successfully"}, status=HTTP_201_CREATED)
        return Response(data={"errors" : serializer.errors} , status=HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="edit the employer information",
        operation_description="change the information of the user if employer exists",
        request_body=EmployerSerializer,
        responses={
            200 : EmployerSerializer,
            404 : "employer was not found",
            403 : "user doesn't have permission to change this data",
        },
        security=[{"Bearer" : []}]
    )
    def patch(self , request) :
        user = request.user
        employer = utils.employer_exists(user)
        
        if not employer :
            return Response(data={"detail" : "employer does not exists"} , status=HTTP_404_NOT_FOUND)
        
        if not user.has_perm('change_employer' , employer) :
            return Response(data={"detail" : "user does not have permission to do this"} , status=HTTP_403_FORBIDDEN)
        
        serializer = EmployerSerializer(employer , data=request.data , partial=True)
        if serializer.is_valid() :
            serializer.save(user=user)
            return Response(data={"data" : serializer.data , "detail " : "employer updated successfully"} , status=HTTP_200_OK)
            
        return Response(data={serializer.errors} , status=HTTP_400_BAD_REQUEST) 

# create cart for the employer

class Cart(APIView) :
    @swagger_auto_schema(
        operation_summary="get the employer cart",
        operation_description="get the cart information of the employer and if there is no cart for this user a active cart will be created",
        responses={
            200 : CartSerializer,
            404 : "employer cart was not found",
            403 : "user doesn't have permission to change this data",
        },
        security=[{"Bearer" : []}]
    )
    # get the cart data
    def get(self , request):
        # add permission to view only their cart
        user = request.user
        employer = utils.employer_exists(user)
        if not employer :
            return Response(data={"detail" : "employer does not exists"} , status=HTTP_404_NOT_FOUND)
        employer_cart = EmployerCart.objects.filter(employer=employer , active = True)
        if not employer_cart.exists() :
            return Response(data={"data" : {}} , status=HTTP_404_NOT_FOUND)
        # check permission of the user
        if not user.has_perm("view_employecart" , employer_cart.first()) :
            return Response(status=HTTP_403_FORBIDDEN)
        serializer = CartSerializer(employer_cart , many=True)
        return Response(data={"data" : serializer.data} , status=HTTP_200_OK)


    @swagger_auto_schema(
        operation_summary="deactivate the employer cart",
        operation_description="deactivate the employer cart",
        responses={
            200 : "successfully",
            404 : "employer/active cart was not found",
            403 : "user doesn't have permission to change this data",
        },
        security=[{"Bearer" : []}]
    )
    # delete the cart virtually
    def delete(self , request):
        user = request.user
        employer = utils.employer_exists(user)
        if not employer :
            return Response(data={"detail" : "employer does not exists"} , status=HTTP_404_NOT_FOUND)
        employer_cart = EmployerCart.objects.filter(employer = employer , active=True)
        if not employer_cart.exists() :
            return Response(data={"detail" : "there is no active cart for this user"} , status=HTTP_404_NOT_FOUND)
        # check permission of the user
        if not user.has_perm("delete_emoloyercart" , employer_cart.first()) :
            return Response(status=HTTP_403_FORBIDDEN)
        employer_cart.update(active = False)
        return Response(data={"detail" : "cart deleted successfully" , "success" : True} , status=HTTP_200_OK)

        

class Cartitems(APIView) :

    @swagger_auto_schema(
        operation_summary="get the employer cart items",
        operation_description="get the cart items for the active cart of the employer",
        responses={
            200: CartItemSerializer,
            404: "employer/active cart was not found",
            403: "user doesn't have permission to change this data",
        },
        security=[{"Bearer": []}]
    )
    def get(self , request) :
        user = request.user
        employer = utils.employer_exists(user)
        if not employer :
            return Response(data={"detail" : "employer does not exists"} , status=HTTP_404_NOT_FOUND)

        try :
            employer_cart = EmployerCart.objects.get(employer = employer , active = True)
        except EmployerCart.DoesNotExist :
            # if there was no active cart
            return Response(data={"data" : {}}, status=HTTP_404_NOT_FOUND)
        
        # check user permission
        if not user.has_perm("view_emoloyercartitems" , employer_cart) :
            return Response(status=HTTP_403_FORBIDDEN)

        data = []
        cart_items = employer_cart.cart_items.all()
        for item in cart_items :
            cart_serializer = CartItemSerializer(item).data
            packages_serialzier = PackageSerializer(item.package).data
            cart_serializer['package'] = packages_serialzier
            data.append(cart_serializer)
        return Response(data={"data" : data} , status=HTTP_200_OK)



    @swagger_auto_schema(
        operation_summary="add cart items to employer active cart",
        operation_description="if there is active cart for the employer add the package to it and if not create the cart then add the package",
        request_body = openapi.Schema(type=openapi.TYPE_OBJECT,properties={"package_id" : openapi.Schema(type=openapi.TYPE_STRING, description="package id")} , required=['package_id']),
        responses={
            200: "successfully",
            400: "invalid parameters",
            404: "employer/active cart was not found",
            403: "user doesn't have permission to change this data",
        },
        security=[{"Bearer": []}]
    )
    def post(self , request) :
        user = request.user
        employer = utils.employer_exists(user)
        package_id = request.data.get('package_id')
        if not package_id :
            return Response(data={"detail" : "package id must be entered"} , status=HTTP_400_BAD_REQUEST)
        if not employer :
            return Response(data={"detail" : "employer does not exists"} , status=HTTP_404_NOT_FOUND)
 
        employer_cart = EmployerCart.objects.filter(employer=employer , active=True)
        if not employer_cart.exists() :
            # if there was no active cart create the cart
            serializer = CartSerializer(data=request.data)
            if serializer.is_valid():
                cart = serializer.save(employer=employer)
                assign_perm("view_employercart" , user , cart )
                assign_perm("change_employercart" , user , cart)
                assign_perm("delete_employercart" , user , cart)
            else :
                return Response(data={"data": serializer.errors}, status=HTTP_400_BAD_REQUEST)

        try :
            package = Package.objects.get(pk=package_id , active=True)
        except Package.DoesNotExist :
            return Response(data={"detail" : "package does not exist"} , status=HTTP_404_NOT_FOUND)

        serializer = CartItemSerializer(data=request.data)

        if serializer.is_valid() :
            cart_item = serializer.save(cart=employer_cart.first() , package=package)
            assign_perm("view_employercartitem" , user , cart_item)
            assign_perm("change_employercartitem" , user , cart_item)
            assign_perm("delete_employercartitem" , user , cart_item)
            return Response(data={"success" : True} , status=HTTP_200_OK)
        return Response(data={"errors" : serializer.errors} , status=HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(
        operation_summary="delete the item from cart",
        operation_description="delete a specific item from a cart",
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            "item_id": openapi.Schema(type=openapi.TYPE_STRING, description="item id")}, required=['package_id']),
        responses={
            200: "successfully",
            400: "invalid parameters",
            404: "employer/item was not found",
            403: "user doesn't have permission to change this data",
        },
        security=[{"Bearer": []}]
    )
    def delete(self , request) :
        user = request.user
        employer = utils.employer_exists(user)
        item_id = request.data.get('item_id')
        if not item_id :
            return Response(data={"detail" : "item id must be entered"} , status=HTTP_400_BAD_REQUEST)
        if not employer :
            return Response(data={"detail" : "employer does not exists"} , status=HTTP_404_NOT_FOUND)

        try :
            cart_item = EmployerCartItem.objects.get(pk=item_id , cart__employer=employer)
        except EmployerCartItem.DoesNotExist :
            return Response(data={"detail" : "item does not exists"} , status=HTTP_404_NOT_FOUND)
        # check user permission
        if not user.has_perm("delete_employercartitems" , cart_item) :
            return Response(status=HTTP_403_FORBIDDEN)
        cart_item.delete()
        return Response(data={"success" : True } , status=HTTP_200_OK)

class Order(APIView) :
    # list of the order by the user
    @swagger_auto_schema(
        operation_summary="get orders data of the employer",
        operation_description="get the list of orders ",
        responses={
            200: OrderSerializer,
            404: "employer/order was not found",
            403: "user doesn't have permission to change this data",
        },
        security=[{"Bearer": []}]
    )
    def get(self, request):
        user = request.user
        employer = utils.employer_exists(user)
        
        if not employer:
            return Response(data={"detail": "Employer does not exist"}, status=HTTP_404_NOT_FOUND)
        # using prefetch cause we want to get all the order items and package datas we use it to decrease the querie
        orders = EmployerOrder.objects.filter(employer=employer).prefetch_related(
            'order_items__package'  #
        ).order_by('order_at')
        
        if not orders.exists():
            return Response(data={"detail": "Order does not exist"}, status=HTTP_404_NOT_FOUND)
        
        # serialize the orders
        data = []
        for order in orders:

            order_data = OrderSerializer(order).data
            
            order_items_data = []
            for item in order.order_items.all():  # 
                order_item_data = OrderItemSerializer(item).data
            
                package_data = PackageSerializer(item.package).data
                order_item_data['package'] = package_data
                
                order_items_data.append(order_item_data)
            order_data['items'] = order_items_data
            data.append(order_data)
        
        return Response(data={"data": data}, status=HTTP_200_OK)


    @swagger_auto_schema(
        operation_summary="create order",
        operation_description="create order and order items for the items in the active cart and the payment is 'completed' ",
        request_body = openapi.Schema(type=openapi.TYPE_OBJECT,properties={"package_id" : openapi.Schema(type=openapi.TYPE_STRING, description="package id")} , required=['package_id']),
        responses={
            200: "successfully",
            400: "invalid parameters",
            404: "employer/cart/cart item was not found",
            403: "user doesn't have permission to change this data",
        },
        security=[{"Bearer": []}]
    )

    def post(self , request):
        pass
        # user = request.user
        # employer = utils.employer_exists(user)
        # if not employer :
        #     return Response(data={"detail" : "employer does not exists"} , status=HTTP_404_NOT_FOUND)
        # # create order and order item base on the items in the employer cart and if it was successfull the cart status will be False
        # # get the items in the cart
        # try :
        #     cart = EmployerCart.objects.get(employer=employer , active=True)
        # except EmployerCart.DoesNotExist :
        #     return Response(data={"detail" : "cart is empty"} , status=HTTP_404_NOT_FOUND)
        # # items in the active cart that will be order
        # items = cart.cart_items.all()
        # if not items :
        #     return Response(data={"detail" : "cart is empty"} , status=HTTP_404_NOT_FOUND)
        # # using transaction atomic to be sure all data will save or nothing
        # with transaction.atomic():
        #     # create the order
        #     order_serializer = OrderSerializer(data=request.data)
        #     if not order_serializer.is_valid():
        #         return Response({"errors": order_serializer.errors}, status=HTTP_400_BAD_REQUEST)
        #     payment = order_serializer.validated_data.get('payment')
        #     # check payment is for the employer
        #     if payment.employer != employer :
        #         return Response(data={"error" : "payment does not belong to this employer"} , status=HTTP_400_BAD_REQUEST)
        #     # if payment is not completed cancel the proccess
        #     if payment.status != "completed" :
        #         return Response(data={"error" : "payment is not completed"} , status=HTTP_400_BAD_REQUEST)
        #     # convert data to a list
        #     order_items_data = [
        #         {
        #             "package": item.package.id,
        #         }
        #         for item in items
        #     ]

        #     item_serializer = OrderItemSerializer(data=order_items_data, many=True)
        #     if not item_serializer.is_valid():
        #         return Response({"errors": item_serializer.errors}, status=HTTP_400_BAD_REQUEST)
        #     # deactivate the Cart and saving the data
        #     order_id = utils.create_random_number()
        #     order = order_serializer.save(employer=employer , order_id = order_id)
        #     item_serializer.save(order=order)
        #     cart.active = False
        #     cart.save()
            
        #     if user.phone :
        #          # send sms for the order
        #         message = Message.objects.create(phone=user.phone ,type="order" , kind="sms")
        #         send_order_sms.apply_async(args=[user.phone , order_id , message.pk])
        #     if user.email : 
        #         # send email for the order 
        #         message = Message.objects.create(email=user.email ,type="order" , kind="email")
        #         send_order_email.apply_async(args=[user.email , order_id , message.pk])
                
        # return Response(data={"errors" : "failed"} , status=HTTP_400_BAD_REQUEST)

class OrderItem(APIView) :
    # list of the order items
    @swagger_auto_schema(
        operation_summary="get the data of order items",
        operation_description="get the data of order items if order/order items exists",
        responses={
            200: OrderItemSerializer,
            400: "invalid parameters",
            404: "employer/order/order item was not found",
            403: "user doesn't have permission to change this data",
        },
        security=[{"Bearer": []}]
    )
    def get(self , request):
        user = request.user
        employer = utils.employer_exists(user)
        order_id = request.data.get('order_id')
        if not order_id :
            return Response(data={"detail" : "order_id must be entered"} , status=HTTP_400_BAD_REQUEST)
        if not employer :
            return Response(data={"detail" : "employer does not exists"} , status=HTTP_404_NOT_FOUND)
        try :
            order = EmployerOrder.objects.get(pk=order_id , employer=employer)
        except EmployerOrder.DoesNotExist :
            return Response(data={"detail" : "order does not exists"} , status=HTTP_404_NOT_FOUND)
        order_items = order.order_items.all()
        if not order_items :
            return Response(data={"detail" : "there is no item for this order"} , status=HTTP_404_NOT_FOUND)
        serializer = OrderItemSerializer(order_items , many=True)
        return Response(data={"data" : serializer.data} , status=HTTP_200_OK)


    
    
class JobOffer(APIView , CountryCityIdMixin) :
    
    @swagger_auto_schema(
        operation_summary="job opportunities that user has made",
        operation_description="the opportunities that user has made",
        responses= { 
            200  : JobOpportunitySerializer,
            400 : "invalid parameters",
            403 :  "user does not have permission to see this data",
            404 :  "employer was not found"
        },
        security=[{"Bearer" : []}]
    )
    def get(self , request):
        user = request.user
        # check for employer exist
        employer = utils.employer_exists(user)
        if not employer :
            return Response(data={"detail" : "employer does not exists"} , status=HTTP_404_NOT_FOUND)
        # check for offers to exist

        job_opportunities = JobOpportunity.objects.filter(employer=employer)
        if not job_opportunities.exists() :
            return Response(data={"detail" : "there is no opportunity for this employer"})
        # if not user.has_perm('view_jobopportunity' , job_opportunities) :
        #     return Response(data={"detail" : "user does not have permissions for this action"} , status=HTTP_403_FORBIDDEN)
        serializer = JobOpportunitySerializer(job_opportunities , many=True)
        return Response(data={"detail" : serializer.data } , status=HTTP_400_BAD_REQUEST)
    
    
    @swagger_auto_schema(
        operation_summary="create the job opportunity",
        operation_description="create job opportunity if the employer exists and have active packages and the permission",
        request_body=JobOpportunitySerializer,
        responses={
            200 : JobOpportunitySerializer,
            400 : "invalid parameters",
            404 : "employer was not found",
            403 : "user doesn't have permission to change this data",
        },
        security=[{"Bearer" : []}]
    )
    def post(self , request) :
        user = request.user
        priority = request.data.get('priority')
        
        if not priority :
            return Response(data={"detail" : "enter the priority"})
        
        # check for employer to exist
        employer = utils.employer_exists(user)
        if not employer :
            return Response(data={"detail" : "employer does not exists"} , status=HTTP_404_NOT_FOUND)
        # check the employer package purchased and order it base on the date of purchase
        purchased_packages = can_create_offer(employer  , priority)
        # check that user can make offer or not
        if not purchased_packages :
            return Response(data={"detail" : "there is no purchase package for this user" , "success" : False} , status=HTTP_404_NOT_FOUND)
        # check the remaining count of request pacakge
        # *implementing this util is wrong cause if the serialzier is be  invalid (for any reason ) the remaining will be minus but the offer will not save*
        if not utils.check_package_remaining(purchased_packages) :
            return Response(data={"detail" : "there is no remaining for this package"} , status=HTTP_404_NOT_FOUND)
        # save the date
        serializer = JobOpportunitySerializer(data=request.data)
        if serializer.is_valid() :
            # adding city and country
            data = self.country_and_city_id(request)
            if isinstance(data , Response):
                return data
            city = data['city']
            country = data['country']
            state = data['state']
            offer = serializer.save(employer=employer , country=country, city=city , state=state)
            purchased_packages.remaining -= 1
            purchased_packages.save()
            message = Message.objects.create(type="expire" , kind="email" , email=user.email)
            warning_eta = offer.expire_at - datetime.timedelta(hours=2)
            tasks.expire_job_offer_warning.apply_async(args=[offer.pk , message.pk] , eta=warning_eta)
            tasks.expire_job_offer.apply_async(args=[offer.pk  ,message.pk] , eta=offer.expire_at)
            # offer.remaining -= 1
            # offer.save()
            # assign permission to the user for its own object
            assign_perm("view_jobopportunity" , user , offer)
            assign_perm("change_jobopportunity" , user , offer)
            assign_perm("delete_jobopportunity" , user , offer)
            return Response(data={"detail" : "Job Opportunity created successfully"} , status=HTTP_201_CREATED)
        return Response(data={"errors" : serializer.errors} , status=HTTP_200_OK)

    
    
    @swagger_auto_schema(
        operation_summary="edit the job opportunity",
        operation_description="edit job opportunity if the employer exists and have active packages and the permission",
        request_body=JobOpportunitySerializer,
        responses={
            200 : JobOpportunitySerializer,
            400 : "invalid parameters",
            404 : "employer was not found",
            403 : "user doesn't have permission to change this data",
        },
        security=[{"Bearer" : []}]
    )
    def patch(self , request) :
        user = request.user
        offer_id = request.data.get('offer_id')
        if not offer_id :
            return Response(data={"detail" : "offer_id must be entered"} , status=HTTP_400_BAD_REQUEST)
        employer = utils.employer_exists(user)
        if not employer :
            return Response(data={"detail" : "employer does not exists"} , status=HTTP_404_NOT_FOUND)
        
        try :
            job_opportunity = JobOpportunity.objects.get(employer=employer , pk=offer_id)
        except JobOpportunity.DoesNotExist :
            return Response(data={"detail" : "not found"} , status=HTTP_404_NOT_FOUND)
        
        if not user.has_perm('view_jobopportunity' , job_opportunity) :
            return Response(data={"detail" : "user does not have permissions for this action"} , status=HTTP_403_FORBIDDEN)
        serializer = JobOpportunitySerializer(job_opportunity , data=request.data , partial=True)
        if serializer.is_valid() :
            serializer.save(employer=employer)
            return Response(data={"data" : serializer.data , "detail" : "job offer updated succesfully"} , status=HTTP_200_OK)
        return Response(data={"errors" : serializer.errors} , status=HTTP_400_BAD_REQUEST)

    
    @swagger_auto_schema(
        operation_summary="delete the job opportunity",
        operation_description="delete job opportunity if the employer exists and have active packages and the permission",
        request_body=JobOpportunitySerializer,
        responses={
            200 : JobOpportunitySerializer,
            400 : "invalid parameters",
            404 : "employer was not found",
            403 : "user doesn't have permission to change this data",
        },
        security=[{"Bearer" : []}]
    )
    def delete(self , request):
        user = request.user
        offer_id = request.data.get('offer_id')
        if not offer_id :
            return Response(data={"detail" : "enter the offer id"} , status=HTTP_400_BAD_REQUEST)
        employer = utils.employer_exists(user)
        if not employer :
            return Response(data={"detail" : "employer does not exists"} , status=HTTP_404_NOT_FOUND)
        if not user.has_perm("delete_jobopportunity") :
            return Response(data={"detail" : "employer does not have permission to do this action"} , status=HTTP_403_FORBIDDEN)
        # delete from db
        # JobOpportunity.objects.get(pk=offer_id).delete()
        # virtual delete
        offer = JobOpportunity.objects.filter(pk=offer_id)
        if not offer.exists() :
            return Response(data={"detail" : "offewr does not exists" } , status=HTTP_400_BAD_REQUEST)
        offer.update(active=False , expire_at = datetime.datetime.now().strftime('%Y-%m-%d'))
        return Response(data={"detail" : "deleted successfully" } , status=HTTP_200_OK)
    
class AllJobOffers(APIView) :

    @swagger_auto_schema(
        operation_summary="get all the job offers",
        operation_description="ge all of the job offers that exist active/not active",
        responses={
            200 : "successfull",
        },
        security=[{"Bearer" : []}]
        )
    def get(self , request):
        job_opportunities = JobOpportunity.objects.all()
        serializer = JobOpportunitySerializer(job_opportunities , many=True)
        return Response(data={"detail" : serializer.data } , status=HTTP_200_OK)
    
    
# view the resume that job seekers sent to the employer for specific job opportunity
class ResumesForOffer(APIView) :
    @swagger_auto_schema(
        operation_summary="view the resume for specific offer",
        operation_description="view the resume that job seekers sent to a offer",
        # request_body=,
        responses={
            200 : ApplicationSerializer,
            400 : "invalid parameters",
            404 : "employer/offer was not found",
        }
    )
    def get(self , request) :
        user = request.user
        offer_id = request.data.get('offer_id')
        # check if employer exists
        if not offer_id :
            return Response(data={"detail" : "offer_id must be enter"} , status=HTTP_400_BAD_REQUEST)
        employer = utils.employer_exists(user)
        if not employer :
            return Response(data={"detail" : "Employer does not exists"} , status=HTTP_404_NOT_FOUND)
        # check if the offer is for the employer
        offer = JobOpportunity.objects.filter(employer=employer , pk=offer_id)
        if not offer.exists() :
            return Response(data={"detail" : "Offer not exists"} , status=HTTP_404_NOT_FOUND)
        # get all resumes
        # ordering in the ascending to show the user latest resume first ( without - )
        applies = Application.objects.filter(job_opportunity=offer.first()).order_by('send_at')
     
        # check if any resume were send to for the offer
        if not applies.exists() :
            return Response(data={"detail" : "there is no apply for this offer yet"} , status=HTTP_404_NOT_FOUND)
        serializer = ApplicationSerializer(applies , many=True)
        return Response(data={"data" : serializer.data} ,status=HTTP_200_OK)
    

class AllResumes(APIView , FilterResumseMixin) : 
    @swagger_auto_schema(
        operation_summary="view all the available resume",
        operation_description="view the all the available resume don't matter they sent it to employer or not",
        # request_body=,
        responses={
            200 : ResumeSerializer,
            400 : "invalid parameters",
            404 : "employer/offer was not found",
        },
        security=[{"Bearer" : []}]
    )
    def get(self , request) :  
        
        user = request.user
        employer = utils.employer_exists(user)
        if not employer :
            return Response(data={"detail" : "Employer does not exists"} , status=HTTP_404_NOT_FOUND)
    
        filtered_resume = self.filter_resume()
        if isinstance(filtered_resume , Response) :
            return filtered_resume
                     
    
            

        paginator = LimitOffsetPagination()
        paginator.paginate_queryset(filtered_resume , request)
        
        serializer = GetResumeSerializer(filtered_resume , many=True)
        return Response(data={"data" : serializer.data} , status=HTTP_200_OK)  
    
    


# transfer the resume to the seen resumes and minus from the remaining 
class ResumeViewer(APIView) :
    @swagger_auto_schema(
        operation_summary="transfer the resume that employer saw to viewed resume",
        operation_description="transfer the resume to the viewed resume to know each employer saw what resumes avoiding duplicate",
        request_body=ViewedResumeSerializer,
        responses={
            200 : "success",
            400 : "invalid parameters",
            404 : "employer/offer was not found",
        },
        security=[{"Bearer" : []}]
    )
    def post(self , request) :
        user = request.user
        employer = utils.employer_exists(user)
        offer_id = request.data.get('offer_id')
        if not offer_id :
            return Response(data={"detail" : "must enter the offer id"} , status=HTTP_400_BAD_REQUEST)

        if not employer :
            return Response(data={"detail" : "Employer Does not exists"} , status=HTTP_404_NOT_FOUND)
        serializer = ViewedResumeSerializer(data=request.data)
        # save the resume for the employer the see what resume 
        if serializer.is_valid() :
            # avoid duplicate for the resume
            data = serializer.validated_data
            resume = data['resume']
            if ViewedResume.objects.filter(employer=employer , resume=resume).exists() :
                return Response(data={"detail" : "Resume was seen before"})

            # check if user have purchased packages or not
            purchased = PurchasedPackage.objects.filter(employer=employer , active=True , package__type="offer").order_by('bought_at')
            if not purchased.exists() :
                return Response(data={"detail" : "employer does not have any purchased packages"})
            # check that the employer have this job offer or not
            try :
                offer = JobOpportunity.objects.get(employer=employer, pk=offer_id)
            except JobOpportunity.DoesNotExist :
                return Response(data={"detail" : "offer does not exists"} , status=HTTP_404_NOT_FOUND)
            # check that the resume is in the job application or not
            try :
                apply = Application.objects.get(job_opportunity=offer , job_seeker__resumes=resume)
            except Application.DoesNotExist :
                return Response(data={"detail" : "apply does not exists"} , status=HTTP_404_NOT_FOUND)

            # change the status of the apply resume to 'seen'
            apply.status = "seen"
            apply.save()
            # save it to the viewed resumes
            serializer.save(employer=employer)
            message = Message.objects.create(type="resume" , kind="email"  , email=user.email)
            tasks.send_resume_status.apply_async(args=[apply.pk , message.pk])
            # minus from the remaining
            purchased_instance = purchased.first()
            new_remaining = purchased_instance.remaining - 1
            purchased_instance.remaining =new_remaining
            purchased_instance.save()

            return Response(data={"success" : True} , status=HTTP_200_OK)
        return Response(data={"success" : False , "errors" : serializer.errors } , status=HTTP_400_BAD_REQUEST)



# employer change the status of the applies
class ChangeApplyStatus(APIView) :
    @swagger_auto_schema(
        operation_summary="update the status of the apply ",
        operation_description="employer can update the status of apply with this options reject/accepet/interview",
        request_body=ChangeApllyStatusSerializer,
        responses={
            200 : "success",
            400 : "invalid parameters",
            404 : "employer/job apply was not found",
        },
        security=[{"Bearer" : []}]
    )
    def patch(self , request) :
        user = request.user 
        apply_id = request.data.get('apply_id') 
        status = request.data.get('status')
        if not status :
            return Response(data={"detail" : "status must be enetered"} , status=HTTP_400_BAD_REQUEST)
        if not apply_id :
            return Response(data={"detail" : "apply_id must be entered"} , status=HTTP_400_BAD_REQUEST)
        employer = utils.employer_exists(user)
        if not employer :
            return Response(data={"detail" : "employer does not exists"} , status=HTTP_404_NOT_FOUND)
        # check that the offer is for the employer or not 
        
        if not user.has_perm("change_application") :
            return Response(data={"error" : "user does not have permission to do this action"} , status=HTTP_403_FORBIDDEN)
        try :
            apply = Application.objects.get(pk=apply_id , job_opportunity__employer=employer)
        except Application.DoesNotExist :
            return Response(data={"detail" : "job apply does not exists"} , status=HTTP_404_NOT_FOUND)   
        
        # change the status of the apply
        serializer = ChangeApllyStatusSerializer(apply , data=request.data , partial=True)
        if serializer.is_valid() :
            status = serializer.validated_data['status']
            serializer.save()
            # create schedule for the apply if the status is interview
            if status == "interview" :
                # check that if there is schedule or not 
                schedule = InterviewSchedule.objects.filter(apply=apply) 
                if schedule.exists() :
                    return Response(data={"error" : "there is schedule for this apply" , "fa_error" : "برنامه برای مصاحبه وجود دارد"} , status=HTTP_400_BAD_REQUEST)
                schedule = InterviewSchedule.objects.create(apply=apply) 
                # give permission to the schedule to the user (employer) and the apply job seeker
                assign_perm("view_interviewschedule" , user , schedule)
                assign_perm("change_interviewschedule" , user , schedule)
                assign_perm("view_interviewschedule" , apply.job_seeker.user , schedule)
                assign_perm("change_interviewschedule" ,  apply.job_seeker.user  , schedule)
            # send the status to the job seeker
            message = Message.objects.create(type="resume" , kind="email"  , email=user.email)
            tasks.send_resume_status.apply_async(args=[apply.pk , message.pk])
            return Response(data={"success" : True , "data" : serializer.data} , status=HTTP_200_OK)
        return Response(data={"errors" : serializer.errors} , status=HTTP_400_BAD_REQUEST)

        
  
class EmployerInterviewSchedule(APIView , InterviewScheduleMixin) :
    @swagger_auto_schema(
        operation_summary="list of employer interview schedules",
        operation_description="employers can get their own schedule",
        responses={
            200 : InterviewScheduleSerializer,
            400 : "invalid parameters",
            403 : "does not have permission",
            404 : "employer was not found",
        },
        security=[{"Bearer" : []}]
    )
    # list of employer interview schedule
    def get(self , request):
        user = request.user
        employer = employer_exists(user)
        if not employer :
            return Response(data={"error" : "employer does not exists"} ,status=HTTP_404_NOT_FOUND )
        # get the schedule base on employer
        interviews = InterviewSchedule.objects.filter(apply__job_opportunity__employer = employer ).exclude(status__in = ["rejected_by_employer" , "rejected_by_jobseeker"])
        serializer = InterviewScheduleSerializer(interviews , many=True)
        return Response(data={"data" : serializer.data} , status=HTTP_200_OK)
    
    
    
    
    @swagger_auto_schema(
        operation_summary="update the interview time of the job apply ",
        operation_description="employer can suggest the time of the interview then if the job seeker accept it will be set as interview time",
        request_body=ChangeInterviewEmployerScheduleSerializer,
        responses={
            200 : "success",
            400 : "invalid parameters",
            403 : "does not have permission",
            404 : "employer/interview/apply was not found",
        },
        security=[{"Bearer" : []}]
    )
    
    def patch(self , request) :
        user = request.user
        
        apply_id = request.data.get("apply_id")
        employer_time = request.data.get("employer_time")
        
        apply = self.check_apply_and_permissions(apply_id ,user , "employer" )
        if isinstance(apply , Response) :
            return apply
        
        interview = self.check_interview(apply)
        if isinstance(interview , Response) :
            return interview
        
        conflict = self.check_conflict(interview.pk , employer_time , apply , "employer")
        if isinstance(conflict , Response) :
            return conflict

        
        serializer = ChangeInterviewEmployerScheduleSerializer(interview ,data=request.data , partial=True)
        if serializer.is_valid() :  
            job_seeker_time = interview.job_seeker_time
            employer_time = serializer.validated_data['employer_time']
            if job_seeker_time :
                if job_seeker_time == employer_time :
                    serializer.validated_data['status'] = 'approved'
                    serializer.validated_data['interview_time'] = job_seeker_time
                if job_seeker_time != employer_time :
                    # interview.job_seeker_time = None
                    serializer.validated_data['status'] = 'rejected_by_employer'
            serializer.save()
                
            return Response(data={"success" : True ,"data" : serializer.data ,"interview_time" :  interview.interview_time } , status=HTTP_200_OK)
        return Response(data={"errors" : serializer.errors} , status=HTTP_400_BAD_REQUEST)
        

  
  
# TODO  add this to admin app    
# for admins
class ChangeJobOfferStatus(APIView) :
    @swagger_auto_schema(
        operation_id="change job offer status",
        operation_summary="change the job opportunity status",
        operation_description="only admins can change the job opportunity status",
        request_body=JobOpportunitySerializer,
        responses={
            200 : JobOpportunitySerializer,
            400 : "invalid parameters",
            404 : "employer/offer was not found",
        },
        security=[{"Bearer" : []}]
    )
    def patch(self , request) :
        user = request.user
        offer_id = request.data.get('offer_id')
        status = request.data.get('status')
        # only admins can change the offer status
        if not user.is_superuser :
            return Response(data={"detail" : "user does not have permission to do this action"} , status=HTTP_403_FORBIDDEN) 
             
        if not offer_id :
            return Response(data={"detail" : "offer_id must be enter"} , status=HTTP_400_BAD_REQUEST)
        
        if not status :
            return Response(data={"detail" : "status must be enter" , "success" : False} , status=HTTP_400_BAD_REQUEST)
        
        job_opportunity = JobOpportunity.objects.filter(pk=offer_id)
        if not job_opportunity.exists() :
            return Response(data={"detail" : "there is no job opportunity with this information"} , status=HTTP_404_NOT_FOUND)
        
        
        serializer = JobOpportunitySerializer(job_opportunity.first() , data=request.data , partial=True)
        if serializer.is_valid() :
            data = serializer.validated_data
            status = data['status']
            # change the active to true if the offer is approved by the admin
            if status == "approved" :
                data['active'] = True
            serializer.save()
            return Response(data={"success" : True , "data" : serializer.data} , status=HTTP_200_OK)
        return Response(data={"success" : False , "errors" : serializer.errors} , status=HTTP_200_OK)

# admins change the price of the package
# the package will be deleted and then with that package info and new price a new package will be created
class ChangePackagePrice(APIView) :
    def post(self , request):
        user = request.user
        package_id = request.data.get('package_id')
        new_price = request.data.get('new_price')
        if not new_price :
            return Response(data={"detail" : "new price must be enetered"} , status=HTTP_400_BAD_REQUEST)
        if not package_id :
            return Response(data={"detail" : "package_id must be entered"} , status=HTTP_400_BAD_REQUEST)
        if not user.is_superuser :
            return Response(data={"detail" : "user does no have permission to do this action"} , status=HTTP_403_FORBIDDEN)
        try :
            package = Package.objects.get(pk = package_id)
        except Package.DoesNotExist :
            return Response(data={"detail" : "package does not exists"} , status=HTTP_404_NOT_FOUND)
        package_data = PackageSerializer(package).data
        package_data['price'] = new_price
        package.active = False
        package.save()
        serializer = PackageSerializer(data=package_data)
        if serializer.is_valid() :
            serializer.save(user=user , active=True)
            return Response(data={"detail" : "success"} , status=HTTP_200_OK)
        return Response(data={"success" : False , "errors" : serializer.errors} , status=HTTP_400_BAD_REQUEST)