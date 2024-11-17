from mmap import error

from django.shortcuts import render
# third party imports
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from guardian.shortcuts import assign_perm
from rest_framework.parsers import MultiPartParser, FormParser
# local imports
from employer.models import JobOpportunity
from .models import JobSeeker, Resume , Application
from .serializers import JobSeekerSerializer, ResumeSerializer , ApplicationSerializer
from account.models import User
from . import utils
# Create your views here.

class JobSeekerRegister(APIView) :
    def get(self, request):
        user = request.user
        # finding the job seeker information
        try :
            job_seeker = JobSeeker.objects.get(user=user)
        except JobSeeker.DoesNotExist :
            return Response(data={"detail" : "there is no job seeker asign to this user"} , status=status.HTTP_404_NOT_FOUND)
        # get the job seeker information
        if not user.has_perm('view_job_seeker' , job_seeker ):
            return Response(data={"detail" : "user does not have permission to view this"} , status=status.HTTP_403_FORBIDDEN)
        serializer = JobSeekerSerializer(job_seeker)
        return Response(data={"detail" : serializer.data}, status=status.HTTP_200_OK)

    def post(self , request):
        user = request.user
        # return if job seeker exists
        if JobSeeker.objects.filter(user=user).exists():
            return Response(data={"detail" : "Job seeker exists for this user"} , status=status.HTTP_400_BAD_REQUEST)
        # register the job seeker
        serializer = JobSeekerSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            data['user'] = user
            job_seeker = serializer.save()
            assign_perm('view_job_seeker' , user , job_seeker )
            assign_perm('change_job_seeker' , user , job_seeker )
            return Response(data={"detail" : "Job Seeker registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(data={"errors" : serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self , request ) :
        user = request.user
        try :
            job_seeker = JobSeeker.objects.get(user=user)
        except JobSeeker.DoesNotExist :
            return Response(data={"detail" : "job seeker does not exists for this user" } , status=status.HTTP_404_NOT_FOUND)

        if not user.has_perm('change_job_seeker' , job_seeker) :
            return Response(data={"detail" : "user does not have permission to do this action"} , status=status.HTTP_403_FORBIDDEN)

        serializer = JobSeekerSerializer(JobSeeker , data=request.data , partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(data={"detail" : "job seeker updated successfully"}, status=status.HTTP_200_OK)
        return Response(data={"errors" : serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class ResumeRegister(APIView) :

    parser_classes = [MultiPartParser] 
    
    def get(self , request):
        user = request.user
        # get the user
        job_seeker = JobSeeker.objects.filter(user=user)

        if not job_seeker :
            return Response(data={"detail" : "there is no job seeker asign to this user"} , status=status.HTTP_404_NOT_FOUND)
        # finding resume base on the job_seeker
        resume = Resume.objects.filter(job_seeker=job_seeker[0])
        # check if the resume exist
        if not resume.exists():
            return Response(data={"detail" : "there is no resume for this job seeker"} , status=status.HTTP_404_NOT_FOUND)
        # have permission to view the resume
        if not user.has_perm('view_resume' , resume[0]) :
            return Response(data={"detail" : "user does not have permission to view this resume"} , status=status.HTTP_403_FORBIDDEN)

        serializer = ResumeSerializer(resume, many=True)
        return Response(data={"detail" : serializer.data}, status=status.HTTP_200_OK)
    
    def post(self , request) :
        user = request.user
        print(request.FILES , request.data)
        job_seeker = JobSeeker.objects.filter(user=user)
        # return if job seeker does not exists
        if not job_seeker :
            return Response(data={"detail" : "there is no job seeker asgin to this user"} , status=status.HTTP_404_NOT_FOUND)
        # return if resume exists
        if Resume.objects.filter(job_seeker=job_seeker[0]).exists() :
            return Response(data={"detail" : "Resume for this job seeker exist . please update it"})
        # create resume
        serializer = ResumeSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            data['job_seeker'] = job_seeker[0]
            resume = serializer.save()
            # assign the basic permission to the user
            # its better handle this in signals cause there is security problem if we create the resume and the assign does not work
            utils.assign_base_permissions(user , resume , "resume")
            return Response(data={"detail" : "resume created successfully"}, status=status.HTTP_201_CREATED)
        return Response(data={"errors" : serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self , request):
        user = request.user
        print(request.data)
        try :
            job_seeker = JobSeeker.objects.get(user=user)
        except JobSeeker.DoesNotExist :
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


    def delete(self , request):
        user = request.user
        try :
            job_seeker = JobSeeker.objects.get(user=user)
        except JobSeeker.DoesNotExist :
            return Response(data={"detail" : "job seeker does not exist"} , status=status.HTTP_404_NOT_FOUND)
        try :
            resume = Resume.objects.get(job_seeker=job_seeker)
        except Resume.DoesNotExist :
            return Response(data={"detail" : "resume does not exist"}, status=status.HTTP_404_NOT_FOUND)
        if not user.has_perm('delete_resume' , resume) :
            return Response(data={"detail" : "user does not have permission to delete resume"} , status=status.HTTP_403_FORBIDDEN)
        resume.delete()
        return Response(data={"detail" : "resume deleted successfully"} , status=status.HTTP_201_CREATED)

class ApplyForJob(APIView):

    def get(self, request):
        user = request.user
        try :
            job_seeker = JobSeeker.objects.get(user=user)
        except User.DoesNotExist:
            return Response(data={"detail" : "user does not exist"} , status=status.HTTP_404_NOT_FOUND)
        applications = Application.objects.filter(job_seeker=job_seeker)
        if not applications.exists() :
            return Response(data={"detail" : "there is no job application that this user has done"} , status=status.HTTP_404_NOT_FOUND)
        if not user.has_perm('view_application' , applications[0]) :
            return Response(data={"detail" "user does not have permission to view this job apply"} , status=status.HTTP_403_FORBIDDEN)
        serializer = ApplicationSerializer(applications, many=True)
        return Response(data={"detail" : serializer.data}, status=status.HTTP_200_OK)

    def post(self , request) :
        user = request.user
        # check that user is asign to job seeker
        try :
            job_seeker = JobSeeker.objects.get(user=user)
        except JobSeeker.DoesNotExist :
            return Response(data={"detail" : "there is no job seeker asign to this user"} , status=status.HTTP_404_NOT_FOUND)

        serializer = ApplicationSerializer(data=request.data)
        if serializer.is_valid() :
            data = serializer.validated_data
            job_opportunity_pk = data['id']
            try :
                job_opportunity = JobOpportunity.objects.get(pk=job_opportunity_pk)
            except JobOpportunity.DoesNotExist :
                return Response(data={"detail"  : "job opportunity with this id does not exist"})
            data['job_seeker'] = job_seeker
            data['job_opportunity'] = job_opportunity
            application = serializer.save()
            # assign the permission to view/delete the offer later
            assign_perm('view_application' , user , application)
            assign_perm('delete_application' , user , application)
            return Response(data={"detail" : "job application was successfull"} , status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self , request):
        user = request.user
        try :
            job_seeker = JobSeeker.objects.get(user=user)
        except User.DoesNotExist:
            return Response(data={"detail" : "user does not exist"} , status=status.HTTP_404_NOT_FOUND)
        applications = Application.objects.filter(job_seeker=job_seeker)
        if not applications.exists() :
            return Response(data={"detail" : "there is no job application that this user has done"} , status=status.HTTP_404_NOT_FOUND)
        if not user.has_perm('delete_application' , applications[0]) :
            return Response(data={"detail" : "user does not have permission to delete this job apply"} , status=status.HTTP_403_FORBIDDEN)
        applications.delete()
        return Response(data={"detail" : "deleted succesfully"} , status=status.HTTP_200_OK)


class AppliesForJob(APIView):
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
    

