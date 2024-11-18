import datetime
from functools import partial
import stat

from django.shortcuts import render

# third party imports
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK , HTTP_201_CREATED , HTTP_400_BAD_REQUEST ,HTTP_401_UNAUTHORIZED , HTTP_403_FORBIDDEN , HTTP_404_NOT_FOUND
from guardian.shortcuts import assign_perm
from account import serializer

# local imports
from .serializers import EmployerSerializer , JobOpportunitySerializer  , ViewedResumeSerializer
from .models import Employer, JobOpportunity, ViewedResume
from job_seeker.utils import assign_base_permissions
from . import utils
from job_seeker.models import Resume , Application
from job_seeker.serializers import ApplicationSerializer, ResumeSerializer
from package.models import PurchasedPackage
# Create your views here.

class EmployerRegister(APIView) :
    def get(self , request):
        user = request.user
        employer = Employer.objects.filter(user=user)
        if not employer.exists():
            return Response(data={"detail" : "there is no employer assign to this user"})
        # check for the user permission
        if not user.has_perm('view_employer' , employer[0]) :
            return Response(data={"detail" : "user does not have permission to view this"} , status=HTTP_403_FORBIDDEN)
        serializer = EmployerSerializer(employer[0])
        return Response(data={"detail" : serializer.data} , status=HTTP_200_OK)


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
        return Response(data={"errors" : serializer.errors} , status=HTTP_200_OK)

    
    def patch(self , request) :
        user = request.user
        try :
            employer = Employer.objects.get(user=user)
        except Employer.DoesNotExist:
            return Response(data={"detail" : "employer does not exists"} , status=HTTP_404_NOT_FOUND)
        
        if not user.has_perm('change_employer' , employer) :
            return Response(data={"detail" : "user does not have permission to do this"} , status=HTTP_403_FORBIDDEN)
        
        serializer = EmployerSerializer(employer , data=request.data , partial=True)
        if serializer.is_valid() :
            serializer.save(user=user)
            return Response(data={"employer updated successfully"} , status=HTTP_200_OK)
            
        return Response(data={serializer.errors} , status=HTTP_400_BAD_REQUEST) 

        

    
    
class JobOffer(APIView) :
    def get(self , request):
        user = request.user
        # check for employer exist
        employer = Employer.objects.filter(user=user)
        if not employer.exists():
            return Response(data={"detail" : "employer does not exists"} , status=HTTP_404_NOT_FOUND)
        # check for offers to exist
        job_opportunities = JobOpportunity.objects.filter(employer=employer[0])
        if not job_opportunities.exists():
            return Response(data={"detail" : "there is no opportunity for this employer"})
        if not user.has_perm('view_jobopportunity' , job_opportunities[0]) :
            return Response(data={"detail" : "user does not have permissions for this action"} , status=HTTP_403_FORBIDDEN)
        serializer = JobOpportunitySerializer(job_opportunities , many=True)
        return Response(data={"detail" : serializer.data } , status=HTTP_200_OK)

    def post(self , request) :
        user = request.user
        package_purchase_id = request.data.get('package_purchase_id')
        
        if not package_purchase_id :
            return Response(data={"detail" : "enter the package_purchase_id"})
        
        # check for employer to exist
        try :
            employer = Employer.objects.get(user=user)
        except Employer.DoesNotExist :
            return Response(data={"detail" : "employer does not exists"} , status=HTTP_404_NOT_FOUND)
        # check that user can make offer or not
        if not utils.can_create_offer(employer , int(package_purchase_id)) :
            return Response(data={"detail" : "there is no purchase package for this user" , "success" : False} , status=HTTP_404_NOT_FOUND)
        # check the remaining count of request pacakge
        # *implementing this util is wrong cause if the serialzier is be  invalid (for any reason ) the remaining will be minus but the offer will not save*
        if not utils.check_package_remaining(employer , int(package_purchase_id)) : 
            return Response(data={"detail" : "there is no remaining for this package"} , status=HTTP_404_NOT_FOUND)
        # save the date
        serializer = JobOpportunitySerializer(data=request.data)
        if serializer.is_valid() :
            offer = serializer.save(employer=employer)
            
            # offer.remaining -= 1
            # offer.save()
            # assign permission to the user for its own object
            assign_perm("view_jobopportunity" , user , offer)
            assign_perm("change_jobopportunity" , user , offer)
            assign_perm("delete_jobopportunity" , user , offer)
            return Response(data={"detail" : "Job Opportunity created successfully"} , status=HTTP_201_CREATED)
        return Response(data={"errors" : serializer.errors} , status=HTTP_200_OK)

    def patch(self , request) :
        user = request.user
        offer_id = request.data.get('offer_id')
        if not offer_id :
            return Response(data={"detail" : "offer_id must be entered"} , status=HTTP_400_BAD_REQUEST)
        try :
            employer = Employer.objects.get(user=user)
        except Employer.DoesNotExist :
            return Response(data={"detail" : "employer does not exists"} , status=HTTP_404_NOT_FOUND)
        
        try :
            job_opportunity = JobOpportunity.objects.get(employer=employer , pk=offer_id)
        except JobOpportunity.DoesNotExist :
            return Response(data={"detail" : "not found"} , status=HTTP_404_NOT_FOUND)
        
        serializer = JobOpportunitySerializer(job_opportunity , data=request.data , partial=True)
        if serializer.is_valid() :
            serializer.save(employer=employer)
            return Response(data={"detail" : "job offer updated succesfully"} , status=HTTP_200_OK)
        return Response(data={"errors" : serializer.errors} , status=HTTP_400_BAD_REQUEST)

    def delete(self , request):
        user = request.user
        offer_id = request.data.get('offer_id')
        if not offer_id :
            return Response(data={"detail" : "enter the offer id"} , status=HTTP_400_BAD_REQUEST)
        try:
            employer = Employer.objects.get(user=user)
        except Employer.DoesNotExist :
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
    def get(self , request):
        job_opportunities = JobOpportunity.objects.all()
        serializer = JobOpportunitySerializer(job_opportunities , many=True)
        return Response(data={"detail" : serializer.data } , status=HTTP_200_OK)
    
    
# see the resume that job seekers sent to the employer for specific    
class ResumesForOffer(APIView) :
    
    def get(self , request) :
        user = request.user
        offer_id = request.data.get('offer_id')
        # check if employer exists
        if not offer_id :
            return Response(data={"detail" : "offer_id must be enter"} , status=HTTP_400_BAD_REQUEST)
        try :
            employer = Employer.objects.get(user=user)
        except Employer.DoesNotExist :
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
    
    def get(self , request) : 
        user = request.user
        try :
            Employer.objects.get(user=user)
        except Employer.DoesNotExist :
            return Response(data={"detail" : "Employer does not exists"} , status=HTTP_404_NOT_FOUND)
        
        resumes = Resume.objects.all()
        if not resumes.exists() :
            return Response(data={"detail" : "there is no resume"} , status=HTTP_404_NOT_FOUND)
        serializer = ResumeSerializer(resumes , many=True)
        return Response(data={"data" : serializer.data} , status=HTTP_200_OK)  
    
    


# transfer the resume to the seen resumes and minus from the remaining 
class ResumeViewer(APIView) :
    def post(self , request) :
        user = request.user
        try :
            employer = Employer.objects.get(user=user)
        except Employer.DoesNotExist :
            return Response(data={"detail" : "Employer Does not exists"} , status=HTTP_404_NOT_FOUND)
        serializer = ViewedResumeSerializer(data=request.data)
        # save the resume for the employer the see what resume 
        if serializer.is_valid() :
            # avoid duplicate for the resume
            data = serializer.validated_data
            resume = data['resume']
            
            if ViewedResume.objects.filter(employer=employer , resume=resume).exists() :
                return Response(data={"detail" : "Resume was seen before"})
            
            serializer.save(employer=employer)
            # check if user have purchased packages or not
            purchased = PurchasedPackage.objects.filter(employer=employer , active=True , package__type=1).order_by('bought_at')
            if not purchased.exists() :
                return Response(data={"detail" : "employer does not have any purchased packages"})
            # minus from the remaining
            purchased_instance = purchased.first()
            new_remaining = purchased_instance.remaining - 1
            purchased_instance.remaining =new_remaining
            purchased_instance.save()
            
            return Response(data={"success" : True} , status=HTTP_200_OK)
        return Response(data={"success" : False , "errors" : serializer.errors } , status=HTTP_400_BAD_REQUEST)

    
    
# for admins
class ChangeJobOfferStatus(APIView) :
    
    def patch(self , request) :
        user = request.user
        offer_id = request.data.get('offer_id')
        status = request.data.get('status')
        
        if not user.is_staff :
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
            serializer.save()
            return Response(data={"success" : True , "data" : serializer.data} , status=HTTP_200_OK)
        return Response(data={"success" : False , "errors" : serializer.errors} , status=HTTP_200_OK)

    