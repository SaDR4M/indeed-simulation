# third party
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
# local
from job_seeker.serializers import ResumeSerializer

resume_register_get_doc = swagger_auto_schema(
        operation_summary="get data resume for the job seeker",
        operation_description="get data resume for the job seeker if job seeker exists and have permission",
        responses={
            200 : ResumeSerializer,
            400 : "invalid parameters",
            404 : "job seeker was not found"
        },
        security=[{"Bearer" : []}]
    )
resume_register_post_doc = swagger_auto_schema(
        operation_summary="register resume for the job seeker",
        operation_description="register resume for the job seeker if job seeker exists",
        request_body=ResumeSerializer,
        responses={
            200 : "resume registered successfully",
            400 : "invalid parameters",
            403 : "does not have permission to do this action",
            404 : "job seeker was not found"
        },
        security=[{"Bearer" : []}]
    )
resume_register_patch_doc = swagger_auto_schema(
        operation_summary="update resume for the job seeker",
        operation_description="update resume for the job seeker if job seeker exists and have the permission",
        request_body=ResumeSerializer,
        responses={
            200 : "resume updated successfully",
            400 : "invalid parameters",
            403 : "does not have permission to do this action",
            404 : "job seeker was not found"
        },
        security=[{"Bearer" : []}]
    )
resume_register_delete_doc = swagger_auto_schema(
        operation_summary="delete resume for the job seeker",
        operation_description="delete resume for the job seeker if job seeker exists",
        responses={
            200 : "resume deleted successfully",
            400 : "invalid parameters",
            403 : "does not have permission to do this action",
            404 : "job seeker was not found"
        },
        security=[{"Bearer" : []}]
    )