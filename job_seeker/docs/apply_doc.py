# third party
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
# local
from job_seeker.serializers import  ApplicationSerializer 


apply_for_job_get_doc = swagger_auto_schema(
        operation_summary="get data about that job seeker job applies",
        operation_description="get the data about job applies that job seeker has done if exists and have permission",
        responses={
            200 : ApplicationSerializer,
            400 : "invalid parameters",
            403 : "does not have permission to do this action",
            404 : "job seeker was not found"
        }
    )

apply_for_job_post_doc = swagger_auto_schema(
        operation_summary="register for job opportunity",
        operation_description="register for job opportunity if job seeker and the offer exists",
        request_body=ApplicationSerializer,
        responses={
            200 : "job application was successfull",
            400 : "invalid parameters",
            404 : "job seeker was not found"
        }
    )


apply_for_job_delete_doc = swagger_auto_schema(
        operation_summary="delete the job apply",
        operation_description="delete the job opportunity if job seeker exists and job seeker has applied for any",
        responses={
            200 : "job application deleted successfully",
            400 : "invalid parameters",
            404 : "job seeker was not found"
        }
    )

applies_for_job_get_doc = swagger_auto_schema(
        operation_summary="get the applies for a specific job offer",
        operation_description="get all the apply for the job opportunity",
        responses={
            200 : ApplicationSerializer,
            400 : "invalid parameters",
            404 : "job seeker was not found"
        }
    )