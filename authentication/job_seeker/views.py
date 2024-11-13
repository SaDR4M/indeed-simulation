from django.shortcuts import render
# third party imports
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import JobSeeker
# local imports
from .serializers import JobSeekerSerializer, ResumeSerializer


# Create your views here.

class JobSeekerRegister(APIView) :
    def get(self, request):
        user = request.user
        # reverse look up for finding the job seeker information
        job_seeker = JobSeeker.objects.filter(user=user)
        if not job_seeker :
            return Response(data={"detail" : "there is no job seeker asign to this user"})

        serializer = JobSeekerSerializer(job_seeker)
        return Response(data={"detail" : serializer.data}, status=status.HTTP_200_OK)

    def post(self , request):
        user = request.user
        if JobSeeker.objects.filter(user=user).exists():
            return Response(data={"detail" : "Job seeker exists"})
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
        # get the user - we can use reverse lookup too
        job_seeker = JobSeeker.objects.get(user=user)
        # reverse lookup for finding resume base on the job_seeker
        resumes = job_seeker.resumes.all()
        serializer = ResumeSerializer(resumes, many=True)
        return Response(data={"detail" : serializer.data}, status=status.HTTP_200_OK)

    def post(self , request) :
        user = request.user
        job_seeker = JobSeeker.objects.get(user=user)
        if job_seeker.resumes.all() :
            return Response(data={"detail" : "Resume for this job seeker exist . please update it"})
        serializer = ResumeSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            data['job_seeker'] = job_seeker
            print(data)
            serializer.save()
            return Response(data={"detail" : "resume created successfully"}, status=status.HTTP_201_CREATED)
        return Response(data={"errors" : serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
