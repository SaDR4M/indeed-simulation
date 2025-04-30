
# third party imports
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser

# local imports
from job_seeker.models import Resume 
from job_seeker.serializers import  ResumeSerializer , GetResumeSerializer 
from job_seeker.utils import create_resume
from job_seeker.decorators import job_seeker_required
from job_seeker.docs import (
    resume_register_get_doc,
    resume_register_post_doc,
    resume_register_patch_doc,
)


# Create your views here.
class ResumeRegister(APIView) :
    parser_classes = [MultiPartParser] 


    @resume_register_get_doc
    @job_seeker_required
    def get(self , request):
        """Job seeker resume data"""
        job_seeker = request.job_seeker
        # finding resume base on the job_seeker
        try :
            resume = Resume.objects.get(job_seeker=job_seeker)
        # check if the resume exist
        except Resume.DoesNotExist :
            return Response(data={"detail" : "there is no resume for this job seeker"} , status=status.HTTP_404_NOT_FOUND)
        # have permission to view the resume
        # if not user.has_perm('view_resume' , resume) :
        #     return Response(data={"detail" : "user does not have permission to view this resume"} , status=status.HTTP_403_FORBIDDEN)
        serializer = GetResumeSerializer(resume)
        return Response(data={"detail" : serializer.data}, status=status.HTTP_200_OK)
    
    
    @resume_register_post_doc
    @job_seeker_required
    def post(self , request) :
        """Create resume for the job seeker"""
        user = request.user
        job_seeker = request.job_seeker
        if Resume.objects.filter(job_seeker=job_seeker).exists() :
            return Response(
                data={
                    "succeeded" : False,
                    "show" : True,
                    'time' : 3000,
                    "en_detail" : "Resume for this job seeker exist . please update it",
                    "fa_detail" : "شما رزومه فعالی دارید در صورت نیاز آن را تغییر دهید"
                }
            )
        # create resume
        stacks = request.data.get('stack').split(',')
        response = create_resume(request , job_seeker , user , stacks)
        return response


    @resume_register_patch_doc
    @job_seeker_required
    def patch(self , request):
        """Update job seeker resume"""
        job_seeker = request.job_seeker
        # get resume
        try :
            resume = Resume.objects.get(job_seeker=job_seeker)
        except Resume.DoesNotExist :
            return Response(data={"detail" : "resume does not exist"} , status=status.HTTP_404_NOT_FOUND)
        # check user permission
        # if not user.has_perm('change_resume' , resume) :
        #     return Response(data={"detail" : "user does not have permission to change this resume"} , status=status.HTTP_403_FORBIDDEN)
        # update the resume
        serializer = ResumeSerializer(resume, data=request.data ,partial=True)
        if serializer.is_valid() :
            serializer.save(job_seeker=job_seeker)
            return Response(data={"detail" : "resume updated successfully"} , status=status.HTTP_200_OK)
        return Response(data={"errors" : serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

