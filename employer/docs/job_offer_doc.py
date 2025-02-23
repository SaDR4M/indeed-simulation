# third party imports
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
# local imports
from employer.serializers import JobOpportunitySerializer


job_offer_get_doc =  swagger_auto_schema(
    operation_summary="job opportunities that user has made",
    operation_description="the opportunities that user has made",
    responses= { 
        200  : JobOpportunitySerializer,
        400 : "invalid parameters",
        403 :  "user does not have permission to see this data",
        404 :  "employer was not found"
    },
    security=[{"Bearer" : []}]
)


job_offer_post_doc = swagger_auto_schema(
    operation_summary="create the job opportunity",
    operation_description="create job opportunity if the employer exists and have active packages and the permission",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "priority" : openapi.Schema(type=openapi.TYPE_STRING ,description="priority of the offer \n options are : \n 1) normal \n 2) urgent"),
            "title" : openapi.Schema(type=openapi.TYPE_STRING , description="title of the job offer"),
            "description" : openapi.Schema(type=openapi.TYPE_STRING , description="description of the job offer"),
            "expire_at" : openapi.Schema(type=openapi.TYPE_STRING , description="date of expiring this offer"),
            "province" : openapi.Schema(type=openapi.TYPE_STRING , description="province of the job offer"),
            "city" : openapi.Schema(type=openapi.TYPE_STRING , description="city of the job offer"),
        },
        required=["title" , "description" , "province" , "city"]
        ),
    responses={
        200 : JobOpportunitySerializer,
        400 : "invalid parameters",
        404 : "employer was not found",
        403 : "user doesn't have permission to change this data",
    },
    security=[{"Bearer" : []}]
)

job_offer_patch_doc = swagger_auto_schema(
    operation_summary="edit the job opportunity",
    operation_description="edit job opportunity if the employer exists and have active packages and the permission",
    request_body=JobOpportunitySerializer,
    responses={
        200 : JobOpportunitySerializer,
        400 : "invalid parameters",
        404 : "employer was not found",
        403 : "user doesn't have permission to change this data",
    },
    security=[{"Bearer" : []}]
)

job_offer_delete_doc = swagger_auto_schema(
    operation_summary="delete the job opportunity",
    operation_description="delete job opportunity if the employer exists and have active packages and the permission",
    request_body=JobOpportunitySerializer,
    responses={
        200 : JobOpportunitySerializer,
        400 : "invalid parameters",
        404 : "employer was not found",
        403 : "user doesn't have permission to change this data",
    },
    security=[{"Bearer" : []}]
)

all_offers_get_doc = swagger_auto_schema(
    operation_summary="get all the job offers",
    operation_description="ge all of the job offers that exist active/not active",
    responses={
        200 : "successfull",
    },
    security=[{"Bearer" : []}]
)