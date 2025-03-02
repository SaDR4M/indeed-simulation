
# third party imports
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
# local imports
from employer.models import JobOpportunity
from job_seeker.models import JobSeeker
from job_seeker.serializers import  UpdateJobSeekerSerializer , JobSeekerDataSerialzier
from job_seeker.utils import register_job_seeker
from job_seeker.decorators import job_seeker_required
from job_seeker.docs import (
    job_seeker_data_patch_doc,
    job_seeker_get_get_doc,
    job_seeker_register_post_doc,
)
# Create your views here.
class JobSeekerData(APIView) : 
    """Get / Update job seeker data"""
    permission_classes = [IsAuthenticated]
    
    @job_seeker_get_get_doc
    @job_seeker_required
    def get(self, request):
        """Job seeker data"""
        # check if user is job seeker
        job_seeker = request.job_seeker
        # get the job seeker information
        # FIXME fix the (AttributeError: 'User' object has no attribute 'has_perm')
        # if not user.has_perm('view_job_seeker' , job_seeker ):
        #     return Response(data={"detail" : "user does not have permission to view this"} , status=status.HTTP_403_FORBIDDEN)
        serializer = JobSeekerDataSerialzier(job_seeker)
        return Response(data={"detail" : serializer.data}, status=status.HTTP_200_OK)
    
    
class JobSeekerRegister(APIView) :
    """Register the job seeker"""
    
    @job_seeker_register_post_doc
    def post(self , request):
        """Register job seeker"""
        user = request.user
        # return if job seeker exists
        if JobSeeker.objects.filter(user=user).exists():
            return Response(data={"detail" : "Job seeker exists for this user"} , status=status.HTTP_400_BAD_REQUEST)
        # register the job seeker
        response = register_job_seeker(request)
        return response


class UpdateJobSeekerApiView(APIView) :

    @job_seeker_data_patch_doc
    @job_seeker_required
    def patch(self , request ) :
        """Update job seeker data"""
        user = request.user
        # check if user is job seeker
        job_seeker = request.job_seeker
        # FIXME fix the permission
        # if not user.has_perm('change_job_seeker' , job_seeker) :
        #     return Response(data={"detail" : "user does not have permission to do this action"} , status=status.HTTP_403_FORBIDDEN)

        serializer = UpdateJobSeekerSerializer(job_seeker , data=request.data , partial=True)
        # TODO fix the location update bug
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(
                data = {
                    "succeeded" : True,
                    "show" : True,
                    "time" : 3000,
                    "en_detail" : "job seeker updated successfully",
                    "fa_detail" : "حساب با موفقیت آپدیت شد"
                },
                status=status.HTTP_200_OK
            )
        return Response(data={"errors" : serializer.errors}, status=status.HTTP_400_BAD_REQUEST)