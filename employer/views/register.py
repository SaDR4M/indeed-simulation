
# django & rest imports
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK , HTTP_201_CREATED , HTTP_400_BAD_REQUEST , HTTP_403_FORBIDDEN , HTTP_404_NOT_FOUND
# third party
from icecream import ic
# local imports
from employer.serializers import (
    EmployerSerializer,
    UpdateEmployerSerializer
)
from employer.models import Employer
from employer.decorators import employer_required
from employer import docs 
from employer.utils import create_employer


# Create your views here.
class EmployerDataApiView(APIView) :
    
    @docs.employer_register_get_doc
    @employer_required
    def get(self , request):
        "Get employer data"
        employer = request.employer
        # check for the user permission
        # FIXME fix the (AttributeError: 'User' object has no attribute 'has_perm')
        # if not user.has_perm('view_employer' , employer) :
        #     return Response(data={"detail" : "user does not have permission to view this"} , status=HTTP_403_FORBIDDEN)
        serializer = EmployerSerializer(employer)
        return Response(
            data={
                "data" : serializer.data
            }, 
            status=HTTP_200_OK
        )


class EmployerRegisterApiView(APIView) :
    
    @docs.employer_register_post_doc
    def post(self , request) :
        # check if the employer exist or not
        user = request.user
        employer = Employer.objects.filter(user=user)

        if employer.exists() :
            return Response(
                data={
                    "succeeded" : False,
                    "show" : True,
                    "time" : 3000,
                    "en_detail" : "Employer exists",
                    "fa_detail" : "کارفرمایی  با این مشخصات وجود دارد"
                } , 
                status=HTTP_400_BAD_REQUEST
                )
        
        response = create_employer(request)
        return response


class EmployerUpdateApiView(APIView) :

    @docs.employer_register_patch_doc
    @employer_required
    def patch(self , request) :
        """Update employer data"""
        
        user = request.user
        employer = request.employer
        ic(request.data)
        # FIXME        
        # if not user.has_perm('change_employer' , employer) :
        #     return Response(data={"detail" : "user does not have permission to do this"} , status=HTTP_403_FORBIDDEN)
        
        serializer = UpdateEmployerSerializer(employer , data=request.data , partial=True)
        if serializer.is_valid() :
            serializer.save(user=user)
            return Response(data={"data" : serializer.data , "detail " : "employer updated successfully"} , status=HTTP_200_OK)
        ic(serializer.errors)
        return Response(
            data = serializer.errors,
            status=HTTP_400_BAD_REQUEST
        ) 