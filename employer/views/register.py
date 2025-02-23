
# third party imports
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK , HTTP_201_CREATED , HTTP_400_BAD_REQUEST , HTTP_403_FORBIDDEN , HTTP_404_NOT_FOUND
from guardian.shortcuts import assign_perm
# local imports
from employer.serializers import (
    EmployerSerializer,
)
from employer.models import Employer
from employer.utils import employer_exists
from employer import docs 
from location.models import Provinces , Cities
from location.utils import get_province , get_city
# Create your views here.

class EmployerRegister(APIView) :
    @docs.employer_register_get_doc
    def get(self , request):
        user = request.user
        employer = employer_exists(user)
        if not employer :
            return Response(data={"detail" : "there is no employer assign to this user"} , status=HTTP_404_NOT_FOUND)
        # check for the user permission
        # FIXME fix the (AttributeError: 'User' object has no attribute 'has_perm')
        # if not user.has_perm('view_employer' , employer) :
        #     return Response(data={"detail" : "user does not have permission to view this"} , status=HTTP_403_FORBIDDEN)
        serializer = EmployerSerializer(employer)
        return Response(data={"data" : serializer.data} , status=HTTP_200_OK)

    @docs.employer_register_post_doc
    def post(self , request) :
        # check if the employer exist or not
        user = request.user
        employer = Employer.objects.filter(user=user)

        if employer.exists() :
            return Response(
                data={
                    "succeeded" : False,
                    "en_detail" : "Employer exists",
                    "fa_detail" : "کارفرمایی  با این مشخصات وجود دارد"
                } , 
                status=HTTP_400_BAD_REQUEST
                )
        
        serializer = EmployerSerializer(data=request.data)
        if serializer.is_valid() :
            # TODO fix this
            province_id = request.data.get('province')
            city_id = request.data.get('city')
            province = get_province(province_id=province_id)
            if isinstance(province , Response) :
                return province
            city = get_city(province_id=province_id , city_id=city_id)
            if isinstance(city , Response) :
                return city
            # adding the user to the validated data
            employer = serializer.save(user=user , city=city, province=province)
            # assign the permission to the user
            assign_perm('view_employer' , user , employer)
            assign_perm('delete_employer' , user , employer)
            # change user role
            user.role = 1
            user.save()
            return Response(data={"detail" : "Employer registered successfully"}, status=HTTP_201_CREATED)
        return Response(data={"errors" : serializer.errors} , status=HTTP_400_BAD_REQUEST)

    @docs.employer_register_patch_doc
    def patch(self , request) :
        user = request.user
        employer = employer_exists(user)
        
        if not employer :
            return Response(data={"detail" : "employer does not exists"} , status=HTTP_404_NOT_FOUND)
        
        if not user.has_perm('change_employer' , employer) :
            return Response(data={"detail" : "user does not have permission to do this"} , status=HTTP_403_FORBIDDEN)
        
        serializer = EmployerSerializer(employer , data=request.data , partial=True)
        if serializer.is_valid() :
            serializer.save(user=user)
            return Response(data={"data" : serializer.data , "detail " : "employer updated successfully"} , status=HTTP_200_OK)
            
        return Response(data={serializer.errors} , status=HTTP_400_BAD_REQUEST) 