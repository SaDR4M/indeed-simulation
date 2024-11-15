from mmap import error

from django.shortcuts import render
# third party imports
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import JobSeeker, Resume , Application
from employer.models import JobOpportunity
# local imports
from .serializers import JobSeekerSerializer, ResumeSerializer , ApplicationSerializer
from account.models import User


# Create your views here.

class JobSeekerRegister(APIView) :
    def get(self, request):
        user = request.user
        # finding the job seeker information
        job_seeker = JobSeeker.objects.filter(user=user)
        if not job_seeker :
            return Response(data={"detail" : "there is no job seeker asign to this user"} , status=status.HTTP_404_NOT_FOUND)
        # get the job seeker information
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
            serializer.save()
            return Response(data={"detail" : "Job Seeker registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(data={"errors" : serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class ResumeRegister(APIView) :

    def get(self , request):
        user = request.user
        # get the user
        job_seeker = JobSeeker.objects.filter(user=user)
        if not job_seeker :
            return Response(data={"detail" : "there is no job seeker asign to this user"} , status=status.HTTP_404_NOT_FOUND)
        # finding resume base on the job_seeker
        resumes = Resume.objects.filter(job_seeker=job_seeker[0])
        if not resumes.exists():
            return Response(data={"detail" : "there is no resume for this job seeker"} , status=status.HTTP_404_NOT_FOUND)
        # get the resume
        serializer = ResumeSerializer(resumes, many=True)
        return Response(data={"detail" : serializer.data}, status=status.HTTP_200_OK)

    def post(self , request) :
        user = request.user
        job_seeker = JobSeeker.objects.filter(user=user)
        # return if job seeker does not exists
        if not job_seeker :
            return Response(data={"detail" : "there is no job seeker asgin to this user"} , status=status.HTTP_404_NOT_FOUND)
        # return if resume exists
        resume = Resume.objects.filter(job_seeker=job_seeker[0])
        if resume.exists() :
            return Response(data={"detail" : "Resume for this job seeker exist . please update it"})
        # create resume
        serializer = ResumeSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            data['job_seeker'] = job_seeker[0]
            serializer.save()
            return Response(data={"detail" : "resume created successfully"}, status=status.HTTP_201_CREATED)
        return Response(data={"errors" : serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ApplyForJob(APIView):
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
            serializer.save()
            return Response(data={"detail" : "job application was successfull"} , status=status.HTTP_201_CREATED)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)   
    
    
    
    
    def get(self, request):
        user = request.user
        try :
            job_seeker = JobSeeker.objects.get(user=user)
        except User.DoesNotExist:
            return Response(data={"detail" : "user does not exist"} , status=status.HTTP_404_NOT_FOUND)
        applications = Application.objects.filter(job_seeker=job_seeker)
        if not applications.exists() :
            return Response(data={"detail" : "there is no job application that this user has done"} , status=status.HTTP_404_NOT_FOUND)
        serializer = ApplicationSerializer(applications, many=True)
        return Response(data={"detail" : serializer.data}, status=status.HTTP_200_OK)


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
    

