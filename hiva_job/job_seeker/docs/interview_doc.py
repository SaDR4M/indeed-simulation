from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
# local
from job_seeker.serializers import ChangeJobSeekerInterviewScheduleSerializer
from employer.serializers import InterviewScheduleSerializer

interview_schedule_get_doc = swagger_auto_schema(
        operation_summary="list of job seeker interview schedules",
        operation_description="job seekers can get their own schedule",
        responses={
            200 : InterviewScheduleSerializer,
            400 : "invalid parameters",
            403 : "does not have permission",
            404 : "job seeker was not found",
        },
        security=[{"Bearer" : []}]
    )

interview_schedule_patch_doc = swagger_auto_schema(
        operation_summary="accept or suggest the interview time of the job apply ",
        operation_description="job seekers can accept or suggest new time instead of the employer time for the interview if employer accept the time it will be set as interview time",
        request_body=ChangeJobSeekerInterviewScheduleSerializer,
        responses={
            200 : "success",
            400 : "invalid parameters",
            403 : "does not have permission",
            404 : "employer/job apply was not found",
        },
        security=[{"Bearer" : []}]
    )