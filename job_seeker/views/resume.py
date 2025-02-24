
# third party imports
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser

# local imports
from job_seeker.models import Resume 
from job_seeker.serializers import  ResumeSerializer , GetResumeSerializer 
from job_seeker import utils
from job_seeker.docs import (
    resume_register_get_doc,
    resume_register_post_doc,
    resume_register_patch_doc,
    resume_register_delete_doc
)

# Create your views here.
class ResumeRegister(APIView) :

    parser_classes = [MultiPartParser] 
    @resume_register_get_doc
    def get(self , request):
        """Job seeker resume data"""
        user = request.user
        # get the user
        job_seeker = utils.job_seeker_exists(user)
        if not job_seeker :
            return Response(data={"detail" : "there is no job seeker asign to this user"} , status=status.HTTP_404_NOT_FOUND)
        # finding resume base on the job_seeker
        try :
            resume = Resume.objects.get(job_seeker=job_seeker)
        # check if the resume exist
        except Resume.DoesNotExist :
            return Response(data={"detail" : "there is no resume for this job seeker"} , status=status.HTTP_404_NOT_FOUND)
        # have permission to view the resume
        if not user.has_perm('view_resume' , resume) :
            return Response(data={"detail" : "user does not have permission to view this resume"} , status=status.HTTP_403_FORBIDDEN)
        serializer = GetResumeSerializer(resume)
        return Response(data={"detail" : serializer.data}, status=status.HTTP_200_OK)
    
    @resume_register_post_doc
    def post(self , request) :
        """Create resume for the job seeker"""
        user = request.user
        print(request.FILES , request.data)
        # return if job seeker does not exists
        job_seeker = utils.job_seeker_exists(user)
        if not job_seeker :
            return Response(data={"detail" : "there is no job seeker asgin to this user"} , status=status.HTTP_404_NOT_FOUND)
        # return if resume exists
        if Resume.objects.filter(job_seeker=job_seeker).exists() :
            return Response(
                data={
                    "succeeded" : False,
                    "show" : True,
                    "en_detail" : "Resume for this job seeker exist . please update it",
                    "fa_detail" : "شما رزومه فعالی دارید در صورت نیاز آن را تغییر دهید"
                }
            )
        # create resume
        serializer = ResumeSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            data['job_seeker'] = job_seeker
            resume = serializer.save()
            # assign the basic permission to the user
            # its better handle this in signals cause there is security problem if we create the resume and the assign does not work
            utils.assign_base_permissions(user , resume , "resume")
            return Response(data={"detail" : "resume created successfully"}, status=status.HTTP_201_CREATED)
        return Response(data={"errors" : serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    @resume_register_patch_doc
    def patch(self , request):
        """Update job seeker resume"""
        user = request.user
        print(request.data)
        job_seeker = utils.job_seeker_exists(user)
        if not job_seeker :
            return Response(data={"detail" : "job seeker does not exist"} , status=status.HTTP_404_NOT_FOUND)
        try :
            resume = Resume.objects.get(job_seeker=job_seeker)
        except Resume.DoesNotExist :
            return Response(data={"detail" : "resume does not exist"} , status=status.HTTP_404_NOT_FOUND)
        if not user.has_perm('change_resume' , resume) :
            return Response(data={"detail" : "user does not have permission to change this resume"} , status=status.HTTP_403_FORBIDDEN)
        serializer = ResumeSerializer(resume, data=request.data ,partial=True)
        if serializer.is_valid() :
            serializer.save(job_seeker=job_seeker)
            return Response(data={"detail" : "resume updated successfully"} , status=status.HTTP_200_OK)
        return Response(data={"errors" : serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    # @resume_register_delete_doc
    # def delete(self , request):
    #     """Delete user's resume"""
    #     user = request.user
    #     job_seeker = utils.job_seeker_exists(user)
    #     if not job_seeker :
    #         return Response(data={"detail" : "job seeker does not exist"} , status=status.HTTP_404_NOT_FOUND)
    #     try :
    #         resume = Resume.objects.get(job_seeker=job_seeker)
    #     except Resume.DoesNotExist :
    #         return Response(data={"detail" : "resume does not exist"}, status=status.HTTP_404_NOT_FOUND)
    #     if not user.has_perm('delete_resume' , resume) :
    #         return Response(data={"detail" : "user does not have permission to delete resume"} , status=status.HTTP_403_FORBIDDEN)
    #     resume.delete()
    #     return Response(data={"detail" : "resume deleted successfully"} , status=status.HTTP_200_OK)
