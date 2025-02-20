# third party
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
# local imports
from employer.serializers import ChangeEmployerInterviewScheduleSerializer
from order.serializers import OrderSerializer

interview_schedule_get_doc = swagger_auto_schema(
        operation_summary="list of employer interview schedules",
        operation_description="employers can get their own schedule",
        manual_parameters=[            
        openapi.Parameter(name="status" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the orders with EXACT package priority. options are : 'normal' , 'urgent' "),
        openapi.Parameter(name="interview_time" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING, description="get the interviews with EXACT interview_time"),
        openapi.Parameter(name="min_interview_time" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the interviews with MIN interview_time"),
        openapi.Parameter(name="max_interview_time" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the interviews with MAX interview_time"),
        openapi.Parameter(name="created_at" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING, description="get the interviews with EXACT created date"),
        openapi.Parameter(name="min_created_at" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the orders with MIN created date(lte)"),
        openapi.Parameter(name="max_created_at" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the orders with MAX created date(gte)"),
        ],
        responses={
            200: OrderSerializer,
            404: "employer/order was not found",
            403: "user doesn't have permission to change this data",
        },
        security=[{"Bearer": []}]
    )
    
interview_schedule_post_doc = swagger_auto_schema(
        operation_summary="update the interview time of the job apply ",
        operation_description="employer can suggest the time of the interview then if the job seeker accept it will be set as interview time",
        request_body=ChangeEmployerInterviewScheduleSerializer,
        responses={
            200 : "success",
            400 : "invalid parameters",
            403 : "does not have permission",
            404 : "employer/interview/apply was not found",
        },
        security=[{"Bearer" : []}]
    )