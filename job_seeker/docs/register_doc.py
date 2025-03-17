# third party
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
# local 
from job_seeker.serializers import JobSeekerSerializer

job_seeker_get_get_doc = swagger_auto_schema(
        operation_summary="Get Job seeker data",
        operation_description="get the current job seeker data if the job seeker exists",
        responses={
            200 : JobSeekerSerializer,
            400 : "invalid parameters",
            403 : "does not have permission to do this action",
            404 : "job seeker was not found"
        },
        security=[{"Bearer" : []}]
    )

job_seeker_data_patch_doc = swagger_auto_schema(
        operation_summary="Update job seeker",
        operation_description="update the current employer data if the job seeker exists",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "gender" : openapi.Schema(type=openapi.TYPE_STRING , description="options are : \n 1) male \n 2) female"),
                "bio" : openapi.Schema(type=openapi.TYPE_STRING , description="job seeker bio"),
                "province_id" : openapi.Schema(type=openapi.TYPE_STRING , description="job seeker province"),
                "city_id" : openapi.Schema(type=openapi.TYPE_STRING , description="job seeker city"),
                "email" : openapi.Schema(type=openapi.TYPE_STRING , description="job seeker email")
            },
            required=[]   
        ),
        responses={
            200 : "updated successfully",
            400 : "invalid parameters",
            403 : "does not have permission to do this action",
            404 : "job seeker was not found"
        },
        security=[{"Bearer" : []}]
    )

job_seeker_register_post_doc = swagger_auto_schema(
        operation_summary="Register job seeker",
        operation_description="register the current employer data if the job seeker does not exists",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "gender" : openapi.Schema(type=openapi.TYPE_STRING , description="user gender : male , female"),
                "bio" : openapi.Schema(type=openapi.TYPE_STRING , description="user bio . a brief description about job seeker"),
                "province" : openapi.Schema(type=openapi.TYPE_INTEGER , description="province id"),
                "city" : openapi.Schema(type=openapi.TYPE_INTEGER , description="city id"),
                
            } ,
            required=["gender" , "province" , "city"]
        ),
        responses={
            200 : "registered successfully",
            400 : "invalid parameters",
            403 : "does not have permission to do this action",
            404 : "job seeker was not found"
        },
    security=[{"Bearer" : []}]
    )