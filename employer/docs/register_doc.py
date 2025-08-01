# third party imports
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
# local imports
from employer.serializers import EmployerSerializer , UpdateEmployerSerializer


employer_register_get_doc = swagger_auto_schema(
    operation_summary="Get employer data",
    operation_description="Get the employer information if the user is employer",
    responses= {
        200 : EmployerSerializer,   
        400 : "invalid parameters",
        403 : "does not have permission to get this data",
        404 : "did't found the employer"
        
    },
    security=[{"Bearer" : []}]
)

employer_register_post_doc = swagger_auto_schema(
    operation_summary="Register employer",
    operation_description="Register the user if this user is not employer",
    request_body= openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "company_name" : openapi.Schema(type=openapi.TYPE_STRING , description="company name"),
            "company_email" : openapi.Schema(type=openapi.TYPE_STRING , description="copmany email address"),
            "address" : openapi.Schema(type=openapi.TYPE_STRING , description="company address"),
            "postal_code" : openapi.Schema(type=openapi.TYPE_STRING , description="company postal code"),
            "id_number" : openapi.Schema(type=openapi.TYPE_STRING , description="compnay register id"),
            "province" : openapi.Schema(type=openapi.TYPE_STRING , description="Province of the employer"),
            "city" : openapi.Schema(type=openapi.TYPE_STRING , description="City of the employer"),
        },
        required=["company_name" , "company_email" , "address" , "postal_code" , "id_number" , "province" , "city"]
        ),
    responses= {
        201 : "employer created successfully",
        400 : "invalid parameters",    
    },
    security=[{"Bearer" : []}]
)

employer_register_patch_doc = swagger_auto_schema(
    operation_summary="Update employer information",
    operation_description="Update the information of the user if employer exists",
    request_body=UpdateEmployerSerializer,
    responses={
        200 : UpdateEmployerSerializer,
        404 : "employer was not found",
        403 : "user doesn't have permission to change this data",
    },
    security=[{"Bearer" : []}]
)


