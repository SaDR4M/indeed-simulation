
# third party imports
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from guardian.shortcuts import assign_perm 
# local imports
from employer.models import JobOpportunity
from job_seeker.models import Application 
from job_seeker.serializers import  ApplicationSerializer 
from job_seeker.utils import apply_for_job
from job_seeker.decorators import job_seeker_required
from job_seeker.docs import (
    applies_for_job_get_doc,
    apply_for_job_post_doc,
    apply_for_job_delete_doc,
    applies_for_job_get_doc
)
# Create your views here.
class ApplyForJob(APIView):

    @applies_for_job_get_doc
    @job_seeker_required
    def get(self, request):
        """Get data of specifc apply"""
        job_seeker = request.job_seeker
        applications = Application.objects.filter(job_seeker=job_seeker)
        if not applications.exists() :
            return Response(data={"detail" : "there is no job application that this user has done"} , status=status.HTTP_404_NOT_FOUND)
        # if not user.has_perm('view_application' , applications) :
        #     return Response(data={"detail" : "user does not have permission to view this job apply"} , status=status.HTTP_403_FORBIDDEN)
        serializer = ApplicationSerializer(applications, many=True)
        return Response(data={"detail" : serializer.data}, status=status.HTTP_200_OK)
    
    
    @apply_for_job_post_doc
    @job_seeker_required
    def post(self , request) :
        "Apply for a job offer"
        
        # check that user is asign to job seeker
        job_seeker = request.job_seeker
        offer_id  = request.data.get('offer_id') 
        if not offer_id :
            return Response(data={"error" : "offer_id must be entered"} , status=status.HTTP_400_BAD_REQUEST)
        # apply for the job
        response = apply_for_job(request , offer_id ,  job_seeker)
        return response

    
    @apply_for_job_delete_doc
    @job_seeker_required
    def delete(self , request):
        """Delete the apply"""
        
        user = request.user
        job_seeker = request.job_seeker
        try :
            applications = Application.objects.get(job_seeker=job_seeker)
        except Application.DoesNotExist :
            return Response(
                data={
                    "succeeded" : False,
                    "en_detail" : "there is no job application that this user has done"
                }, 
                status=status.HTTP_404_NOT_FOUND
            )
        # FIXME
        # if not user.has_perm('delete_application' , applications) :
        #     return Response(data={"detail" : "user does not have permission to delete this job apply"} , status=status.HTTP_403_FORBIDDEN)
        applications.delete()
        return Response(data={"detail" : "deleted succesfully"} , status=status.HTTP_200_OK)


class AppliesForJob(APIView):
        
    @applies_for_job_get_doc
    def get(self , request) :
        """list of applies for a specific job offer"""
        
        job_id = request.data.get('id')
        # check that offer exists or not
        try :
            job_opportunity = JobOpportunity.objects.get(pk=job_id)
        except JobOpportunity.DoesNotExist :
            return Response(
                data={
                    "succeeded" : False,
                    "en_detail" : "Job opportunity does not exist"
                }, 
                status=status.HTTP_404_NOT_FOUND
            )
        applications = Application.objects.filter(job_opportunity=job_opportunity)
        # if job seeker applied for this offer before
        if not applications.exists() :
            return Response(
                data={
                    "succeeded" : False,
                    "show" : True,
                    "time" : 3000,
                    "en_detail" : "You have already applied for this job",
                    "fa_detail" :"شما برای این موقعیت شغلی درخواست داده بودید",
                    
                }, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ApplicationSerializer(applications, many=True)
        return Response(data={"detail" : serializer.data}, status=status.HTTP_200_OK)