import datetime
from functools import partial

# third party imports
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK , HTTP_201_CREATED , HTTP_400_BAD_REQUEST ,HTTP_401_UNAUTHORIZED , HTTP_403_FORBIDDEN , HTTP_404_NOT_FOUND
from guardian.shortcuts import assign_perm
from account import serializer
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from package.serializers import PackageSerializer
# local imports
from .serializers import (EmployerSerializer , 
                          JobOpportunitySerializer  , 
                          ViewedResumeSerializer , 
                          ChangeApllyStatusSerializer ,
                          CreateCartSerializer,
                          CreateCartItemSerializer,
                        )
                          
from .models import Employer, JobOpportunity, ViewedResume , EmployerCart , EmployerCartItems
from job_seeker.utils import assign_base_permissions
from . import utils
from job_seeker.models import Resume , Application
from job_seeker.serializers import ApplicationSerializer, ResumeSerializer
from package.models import PurchasedPackage, Package
from .utils import can_create_offer, employer_exists


# Create your views here.

class EmployerRegister(APIView) :
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
            # adding the user to the validated data
            employer = serializer.save(user=user)
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
            400 : "invalid parameters",
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
    def get():
        pass     
    
    
    def post(self , request) :
        user = request.user
        employer = utils.employer_exists(user)
        if not employer :
            return Response(data={"detail" : "employer does not exists"} , status=HTTP_404_NOT_FOUND)
        employer_cart = EmployerCart.objects.filter(employer = employer , active=True)
        if employer_cart.exists() :
            return Response(data={"detail" : "there is active cart for this user"} , status=HTTP_400_BAD_REQUEST)
        serializer = CreateCartSerializer(data=request.data)
        if serializer.is_valid() :
  
            serializer.save() 
            return Response(data={"success"  : True } , status=HTTP_201_CREATED)
        return Response(data={"errors" : serializer.errors} , status=HTTP_400_BAD_REQUEST)
        

        

class Cartitems(APIView) :
    def get() :
        pass
    
    def post(self , request) :
        user = request.user
        employer = utils.employer_exists(user)
        if not employer :
            return Response(data={"detail" : "employer does not exists"} , status=HTTP_404_NOT_FOUND)
        try :
            employer_cart = EmployerCart.objects.get(employer=employer , active=True)
        except EmployerCart.DoesNotExist :
            return Response(data={"detail" : "cart does no exists"} ,  status=HTTP_404_NOT_FOUND)
        
        serializer = CreateCartItemSerializer(data=request.data)
        if serializer.is_valid() :
            serializer.save()
            serializer.validated_data['user'] = user
            serializer.validated_data['cart'] = employer_cart
            return Response(data={"success" : True} , status=HTTP_200_OK)
        return Response(data={"errors" : serializer.errors} , status=HTTP_400_BAD_REQUEST)   
    
    def patch() :
        pass
    
    def delete() :
        pass
# add item to cart

    
    
class JobOffer(APIView) :
    
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
            offer = serializer.save(employer=employer)
            purchased_packages.remaining -= 1
            purchased_packages.save()
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
            404 : "employer/offeer was not found",
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
    

class AllResumes(APIView) : 
    @swagger_auto_schema(
        operation_summary="view all the available resume",
        operation_description="view the all the available resume don't matter they sent it to employer or not",
        # request_body=,
        responses={
            200 : ResumeSerializer,
            400 : "invalid parameters",
            404 : "employer/offeer was not found",
        },
        security=[{"Bearer" : []}]
    )
    def get(self , request) : 
        user = request.user
        employer = utils.employer_exists(user)
        if not employer :
            return Response(data={"detail" : "Employer does not exists"} , status=HTTP_404_NOT_FOUND)
        
        resumes = Resume.objects.all()
        if not resumes.exists() :
            return Response(data={"detail" : "there is no resume"} , status=HTTP_404_NOT_FOUND)
        serializer = ResumeSerializer(resumes , many=True)
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
            404 : "employer/offeer was not found",
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
            # minus from the remaining
            purchased_instance = purchased.first()
            new_remaining = purchased_instance.remaining - 1
            purchased_instance.remaining =new_remaining
            purchased_instance.save()

            return Response(data={"success" : True} , status=HTTP_200_OK)
        return Response(data={"success" : False , "errors" : serializer.errors } , status=HTTP_400_BAD_REQUEST)



# employer change the status of the applies
class ChangeApplyStatus(APIView) :
    
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
        try :
            apply = Application.objects.get(pk=apply_id , job_opportunity__employer=employer)
        except Application.DoesNotExist :
            return Response(data={"detail" : "job apply does not exists"} , status=HTTP_404_NOT_FOUND)   
        
        # change the status of the apply
        serializer = ChangeApllyStatusSerializer(apply , data=request.data , partial=True)
        if serializer.is_valid() :
            serializer.save()
            return Response(data={"success" : True , "data" : serializer.data} , status=HTTP_200_OK)
        return Response(data={"errors" : serializer.errors} , status=HTTP_400_BAD_REQUEST)


    
    
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
            404 : "employer/offeer was not found",
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