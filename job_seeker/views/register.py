
# third party imports
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
# local imports
from employer.models import JobOpportunity
from job_seeker.models import JobSeeker
from job_seeker.serializers import JobSeekerSerializer
from job_seeker import utils
from job_seeker.docs import (
    job_seeker_register_get_doc,
    job_seeker_register_post_doc,
    job_seeker_register_patch_doc,
)
from location.utils import get_city , get_province
# Create your views here.
class JobSeekerRegister(APIView) :
    @job_seeker_register_get_doc
    def get(self, request):
        user = request.user
        # finding the job seeker information
        job_seeker = utils.job_seeker_exists(user)
        if not job_seeker :
            return Response(data={"detail" : "there is no job seeker assigned to this user"} , status=status.HTTP_404_NOT_FOUND)
        # get the job seeker information
        # FIXME fix the (AttributeError: 'User' object has no attribute 'has_perm')
        # if not user.has_perm('view_job_seeker' , job_seeker ):
        #     return Response(data={"detail" : "user does not have permission to view this"} , status=status.HTTP_403_FORBIDDEN)
        serializer = JobSeekerSerializer(job_seeker)
        return Response(data={"detail" : serializer.data}, status=status.HTTP_200_OK)
    
    
    @job_seeker_register_post_doc
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
            # adding the city and country
            province_id = request.data.get('province')
            province = get_province(province_id=province_id)
            if isinstance(province , Response) :
                return province
            
            city_id = request.data.get('city')
            city = get_city(province_id=province_id , city_id=city_id)
            if isinstance(city , Response) :
                return city
            
            job_seeker = serializer.save(user=user , city=city , province=province)
            # assign base permission
            utils.assign_base_permissions(user, job_seeker, "jobseeker")
            # change user role
            user.role = 2
            user.save()
            return Response(data={"detail" : "Job Seeker registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(data={"errors" : serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    @job_seeker_register_patch_doc
    def patch(self , request ) :
        user = request.user
        job_seeker = utils.job_seeker_exists(user)
        if not job_seeker :
            return Response(data={"detail" : "job seeker does not exists for this user" } , status=status.HTTP_404_NOT_FOUND)

        if not user.has_perm('change_job_seeker' , job_seeker) :
            return Response(data={"detail" : "user does not have permission to do this action"} , status=status.HTTP_403_FORBIDDEN)

        serializer = JobSeekerSerializer(job_seeker , data=request.data , partial=True)
        # TODO fix the location update bug
        if serializer.is_valid():
            # country_data = self.country_and_city_id(request)
            # if isinstance(country_data , Response):
            #     return country_data
            # city = country_data['city']
            # country = country_data['country']
            # state = country_data['state']
            # serializer.save(user=user , city=city , country=country , state=state)
            serializer.save(user=user)
            return Response(data={"detail" : "job seeker updated successfully"}, status=status.HTTP_200_OK)
        return Response(data={"errors" : serializer.errors}, status=status.HTTP_400_BAD_REQUEST)