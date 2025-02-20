
# third party imports
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from guardian.shortcuts import assign_perm 
# local imports
from employer.models import JobOpportunity
from employer.models import Application 
from employer.serializers import  ApplicationSerializer 
from employer import utils
from job_seeker.docs import (
    applies_for_job_get_doc,
    apply_for_job_post_doc,
    apply_for_job_delete_doc,
    applies_for_job_get_doc
)
# Create your views here.
class ApplyForJob(APIView):

    @applies_for_job_get_doc
    def get(self, request):
        user = request.user 
        job_seeker = utils.job_seeker_exists(user)
        if not job_seeker :
            return Response(data={"detail" : "user does not exist"} , status=status.HTTP_404_NOT_FOUND)

        applications = Application.objects.filter(job_seeker=job_seeker)
        if not applications.exists() :
            return Response(data={"detail" : "there is no job application that this user has done"} , status=status.HTTP_404_NOT_FOUND)
        # if not user.has_perm('view_application' , applications) :
        #     return Response(data={"detail" : "user does not have permission to view this job apply"} , status=status.HTTP_403_FORBIDDEN)
        serializer = ApplicationSerializer(applications, many=True)
        return Response(data={"detail" : serializer.data}, status=status.HTTP_200_OK)
    
    @apply_for_job_post_doc
    def post(self , request) :
        user = request.user
        # check that user is asign to job seeker
        job_seeker = utils.job_seeker_exists(user)
        if not job_seeker :
            return Response(data={"error" : "there is no job seeker asign to this user"} , status=status.HTTP_404_NOT_FOUND)
        offer_id  = request.data.get('offer_id') 
        if not offer_id :
            return Response(data={"error" : "offer_id must be entered"} , status=status.HTTP_400_BAD_REQUEST)
        
        

        serializer = ApplicationSerializer(data=request.data)
        
        if serializer.is_valid() :
            data = serializer.validated_data
            try :
                job_opportunity = JobOpportunity.objects.get(pk=offer_id , status="approved")
            except JobOpportunity.DoesNotExist :
                return Response(data={"error"  : "job opportunity does not exist"})
            
            apply = Application.objects.filter(job_seeker=job_seeker , job_opportunity=job_opportunity)
            
            if apply.exists() : 
                return Response(data={"error" : "job seeker applied for this job before"} , status=status.HTTP_400_BAD_REQUEST)
            
            data['job_seeker'] = job_seeker
            data['job_opportunity'] = job_opportunity
   
            application = serializer.save()
            # assign the permission to view/delete the offer later
            assign_perm('view_application' , user , application)
            assign_perm('delete_application' , user , application)
            assign_perm('view_application' , job_opportunity.employer.user , application)
            assign_perm('change_application' , job_opportunity.employer.user , application)
            return Response(data={"detail" : "job application was successfull"} , status=status.HTTP_201_CREATED)

        return Response(data={"errors" : serializer.errors} , status=status.HTTP_400_BAD_REQUEST)
    

    # wrong code
    @apply_for_job_delete_doc
    def delete(self , request):
        user = request.user
        job_seeker = utils.job_seeker_exists(user)
        if not job_seeker :
            return Response(data={"detail" : "user does not exist"} , status=status.HTTP_404_NOT_FOUND)
        try :
            applications = Application.objects.get(job_seeker=job_seeker)
        except Application.DoesNotExist :
            return Response(data={"detail" : "there is no job application that this user has done"} , status=status.HTTP_404_NOT_FOUND)
        if not user.has_perm('delete_application' , applications) :
            return Response(data={"detail" : "user does not have permission to delete this job apply"} , status=status.HTTP_403_FORBIDDEN)
        applications.delete()
        return Response(data={"detail" : "deleted succesfully"} , status=status.HTTP_200_OK)


class AppliesForJob(APIView):
        
    @applies_for_job_get_doc
    def get(self , request) :
        job_id = request.data.get('id')
        try :
            job_opportunity = JobOpportunity.objects.get(pk=job_id)
        except JobOpportunity.DoesNotExist :
            return Response(data={"detail" : "job opportunity with this job id does not exist"} , status=status.HTTP_404_NOT_FOUND)
        applications = Application.objects.filter(job_opportunity=job_opportunity)
        if not applications.exists() :
            return Response(data={"detail" : "there is apply for this job"} , status=status.HTTP_404_NOT_FOUND)
        serializer = ApplicationSerializer(applications, many=True)
        return Response(data={"detail" : serializer.data}, status=status.HTTP_200_OK)