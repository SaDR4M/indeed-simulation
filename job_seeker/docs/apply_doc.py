# third party
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
# local
from job_seeker.serializers import  ApplicationSerializer 


apply_for_job_get_doc = swagger_auto_schema(
        operation_summary="Get apply data",
        operation_description="get the data about job applies that job seeker has done if exists and have permission",
        responses={
            200 : ApplicationSerializer,
            400 : "invalid parameters",
            403 : "does not have permission to do this action",
            404 : "job seeker was not found"
        }
    )

apply_for_job_post_doc = swagger_auto_schema(
        operation_summary="Apply for offer",
        operation_description="register for job opportunity if job seeker and the offer exists",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "offer_id" : openapi.Schema(type=openapi.TYPE_INTEGER , description="Job opportunity id"),
                "description" : openapi.Schema(type=openapi.TYPE_STRING , description="Description of apply")
            },
            required=[] 
        ),
        responses={
            200 : "job application was successfull",
            400 : "invalid parameters",
            404 : "job seeker was not found"
        }
    )


apply_for_job_delete_doc = swagger_auto_schema(
        operation_summary="Delete apply",
        operation_description="delete the job opportunity if job seeker exists and job seeker has applied for any",
        responses={
            200 : "job application deleted successfully",
            400 : "invalid parameters",
            404 : "job seeker was not found"
        }
    )

applies_for_job_get_doc = swagger_auto_schema(
        operation_summary="Get list of applies for a offer",
        operation_description="get all the apply for the job opportunity",
        responses={
            200 : ApplicationSerializer,
            400 : "invalid parameters",
            404 : "job seeker was not found"
        }
    )