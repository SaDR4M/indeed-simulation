# third party
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
# local
from employer.serializers import (
                        ViewedResumeSerializer,
                        GetViewedResumeSerializer,
                        ChangeApllyStatusSerializer,
                        GetAppliedViewedResumeSerializer
                          )
from job_seeker.serializers import ApplicationSerializer, GetResumeSerializer

resume_for_offer_get_doc = swagger_auto_schema(
        operation_summary="view the resume for specific offer",
        operation_description="view the resume that job seekers sent to a offer",
        # request_body=,
        responses={
            200 : ApplicationSerializer,
            400 : "invalid parameters",
            404 : "employer/offer was not found",
        }
    )

all_resume_get_doc =  swagger_auto_schema(
        operation_summary="view all the available resume",
        operation_description="view the all the available resume don't matter they sent it to employer or not",
        manual_parameters=[
            openapi.Parameter(
                'experience', openapi.IN_QUERY, description="EAXCT years of experience ", type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'experience_min', openapi.IN_QUERY, description="Minimum years of experience", type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'experience_max', openapi.IN_QUERY, description="Maximum years of experience", type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(name="created_at" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING, description="get the resume with this EXACT created date time (for having range date time you must define max and min created date time together)"),
            openapi.Parameter(name="min_created_at" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the resume with MIN created date time (lte)"),
            openapi.Parameter(name="max_created_at" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the resume with MAX created date time  (gte)"),
            openapi.Parameter(
                'age', openapi.IN_QUERY, description="Age range (min_age,max_age)", type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'skills', openapi.IN_QUERY, description="Skills to filter by (JSON format)", type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'gender', openapi.IN_QUERY, description="Gender (exact match)", type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'city', openapi.IN_QUERY, description="City to filter by (exact match)", type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'province', openapi.IN_QUERY, description="Province to filter by (exact match)", type=openapi.TYPE_STRING
            ),
        ],
        # request_body=,
        responses={
            200 : GetResumeSerializer,
            400 : "invalid parameters",
            404 : "employer/offer was not found",
        },
        security=[{"Bearer" : []}]
    )

resume_viewer_get_doc = swagger_auto_schema(
        operation_summary="get all viewed resume by employer",
        operation_description="get all resume that employer viewed them",
        manual_parameters=[
                
            openapi.Parameter(
                'experience', openapi.IN_QUERY, description="EAXCT years of experience ", type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'experience_min', openapi.IN_QUERY, description="Minimum years of experience", type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'experience_max', openapi.IN_QUERY, description="Maximum years of experience", type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(name="resume_created_at" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING, description="get the resume with this EXACT created date time (for having range date time you must define max and min created date time together)"),
            openapi.Parameter(name="resume_min_created_at" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the resume with MIN created date time (lte)"),
            openapi.Parameter(name="resume_max_created_at" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the resume with MAX created date time  (gte)"),
            openapi.Parameter(name='seen_at' , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the resume with EXACT seen date "),
            openapi.Parameter(name='min_seen_at' , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the resume with MIN seen date"),
            openapi.Parameter(name='max_seen_at' , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the resume with MAX seen date"),
            openapi.Parameter(
                'age', openapi.IN_QUERY, description="Age range (min_age,max_age)", type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'skills', openapi.IN_QUERY, description="Skills to filter by (JSON format)", type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'gender', openapi.IN_QUERY, description="Gender (exact match)", type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'city', openapi.IN_QUERY, description="City to filter by (exact match)", type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'province', openapi.IN_QUERY, description="Province to filter by (exact match)", type=openapi.TYPE_STRING
            )
        ],
        # request_body=,
        responses={
            200 : GetViewedResumeSerializer,
            400 : "invalid parameters",
            404 : "employer was not found",
        },
        security=[{"Bearer" : []}]
    )


resume_viewer_post_doc = swagger_auto_schema(
        operation_summary="transfer the resume that employer saw to viewed resume",
        operation_description="transfer the resume to the viewed resume to know each employer saw what resumes avoiding duplicate",
        request_body=ViewedResumeSerializer,
        responses={
            200 : "success",
            400 : "invalid parameters",
            404 : "employer/job opportunity/job apply was not found",
        },
        security=[{"Bearer" : []}]
    )

applied_resume_viewer_get_doc = swagger_auto_schema(
        operation_summary="get all applied resume that are viewed by employer",
        operation_description="get all applied resume that are viewed by employer . it can be filtered base on the resume , apply , job offer name",
        manual_parameters=[
                
            openapi.Parameter(
                'experience', openapi.IN_QUERY, description="EAXCT years of experience ", type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'experience_min', openapi.IN_QUERY, description="Minimum years of experience", type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'experience_max', openapi.IN_QUERY, description="Maximum years of experience", type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(name="resume_created_at" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING, description="get the resume with this EXACT created date time (for having range date time you must define max and min created date time together)"),
            openapi.Parameter(name="resume_min_created_at" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the resume with MIN created date time (lte)"),
            openapi.Parameter(name="resume_max_created_at" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the resume with MAX created date time  (gte)"),
            openapi.Parameter(name='seen_at' , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the resume with EXACT seen date "),
            openapi.Parameter(name='min_seen_at' , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the resume with MIN seen date"),
            openapi.Parameter(name='max_seen_at' , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the resume with MAX seen date"),
            openapi.Parameter(
                'age', openapi.IN_QUERY, description="Age range (min_age,max_age)", type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'skills', openapi.IN_QUERY, description="Skills to filter by (JSON format)", type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'gender', openapi.IN_QUERY, description="Gender (exact match)", type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'city', openapi.IN_QUERY, description="City to filter by (exact match)", type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'province', openapi.IN_QUERY, description="Province to filter by (exact match)", type=openapi.TYPE_STRING
            ),          
            openapi.Parameter(
                'job_offer_name', openapi.IN_QUERY, description="viewed applied resume that CONTAINS (in case sensitive) job offer name ", type=openapi.TYPE_INTEGER
            ),
        ],
        # request_body=,
        responses={
            200 : GetAppliedViewedResumeSerializer,
            400 : "invalid parameters",
            403 : "does not have permission",
            404 : "employer/job opportunity/apply was not found",   
        },
        security=[{"Bearer" : []}]
    )
applied_resume_viewer_post_doc = swagger_auto_schema(
        operation_summary="add the applied resume to employer viewed resume",
        operation_description="add the applied resume to employer viewed resume ** this is different that the viewed resume this is only for the resume that are applied for employer job offers**",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'offer_id'  : openapi.Schema(type=openapi.TYPE_INTEGER , description="the offer_id of that resume applied to"),
                'apply_id' : openapi.Schema(type=openapi.TYPE_INTEGER , description="the apply_id of that resume applied to"),
            },
            required=['offer_id' , 'apply_id'],
        ),
        responses={
            200: "success",
            400 : "invalid paramters",
            404 : "offer/apply was not found"
        },
        security=[{"Bearer" : []}]
        
    )


change_apply_status_patch_doc = swagger_auto_schema(
        operation_summary="update the status of the apply ",
        operation_description="employer can update the status of apply with this options reject/accepet/interview",
        request_body=ChangeApllyStatusSerializer,
        responses={
            200 : "success",
            400 : "invalid parameters",
            404 : "employer/job apply was not found",
        },
        security=[{"Bearer" : []}]
    )