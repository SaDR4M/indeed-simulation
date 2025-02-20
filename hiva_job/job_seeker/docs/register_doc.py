# third party
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
# local 
from job_seeker.serializers import JobSeekerSerializer

job_seeker_register_get_doc = swagger_auto_schema(
        operation_summary="get the current job seeker data",
        operation_description="get the current job seeker data if the job seeker exists",
        responses={
            200 : JobSeekerSerializer,
            400 : "invalid parameters",
            403 : "does not have permission to do this action",
            404 : "job seeker was not found"
        }
    )
job_seeker_register_post_doc = swagger_auto_schema(
        operation_summary="register job seeker",
        operation_description="register the current employer data if the job seeker does not exists",
        request_body=JobSeekerSerializer,
        responses={
            200 : "registered successfully",
            400 : "invalid parameters",
            403 : "does not have permission to do this action",
            404 : "job seeker was not found"
        }
    )
job_seeker_register_patch_doc = swagger_auto_schema(
        operation_summary="update job seeker",
        operation_description="update the current employer data if the job seeker exists",
        request_body=JobSeekerSerializer,
        responses={
            200 : "updated successfully",
            400 : "invalid parameters",
            403 : "does not have permission to do this action",
            404 : "job seeker was not found"
        }
    )