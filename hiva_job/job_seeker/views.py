import datetime
from django.shortcuts import render
# third party imports
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from guardian.shortcuts import assign_perm , get_objects_for_user
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.pagination import LimitOffsetPagination
# local imports
from employer.models import JobOpportunity
from .models import JobSeeker, Resume , Application , Test , Question , Answer
from .serializers import JobSeekerSerializer, ResumeSerializer , ApplicationSerializer , TestSerializer , GetResumeSerializer , GetJobSeekerSerialzier , ChangeInterviewJobSeekerScheduleSerializer , QuestionSerializer , AnswerSerializer
from account.models import User
from . import utils
from employer.serializers import InterviewScheduleSerializer
from employer.models import InterviewSchedule  
from employer.mixins import InterviewScheduleMixin, FilterInterviewScheduleMixin 
from job_seeker.mixins import JobSeekerFilterMixin , FilterTestMixin , FilterQuestionMixin
# Create your views here.

class JobSeekerRegister(APIView) :
    @swagger_auto_schema(
        operation_summary="get the current job seeker data",
        operation_description="get the current job seeker data if the job seeker exists",
        responses={
            200 : JobSeekerSerializer,
            400 : "invalid parameters",
            403 : "does not have permission to do this action",
            404 : "job seeker was not found"
        }
    )
    def get(self, request):
        user = request.user
        # finding the job seeker information
        job_seeker = utils.job_seeker_exists(user)
        if not job_seeker :
            return Response(data={"detail" : "there is no job seeker asign to this user"} , status=status.HTTP_404_NOT_FOUND)
        # get the job seeker information
        if not user.has_perm('view_job_seeker' , job_seeker ):
            return Response(data={"detail" : "user does not have permission to view this"} , status=status.HTTP_403_FORBIDDEN)
        serializer = JobSeekerSerializer(job_seeker)
        return Response(data={"detail" : serializer.data}, status=status.HTTP_200_OK)
    
    
    
    
    @swagger_auto_schema(
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
    def post(self , request):
        user = request.user
        # return if job seeker exists
        if JobSeeker.objects.filter(user=user).exists():
            return Response(data={"detail" : "Job seeker exists for this user"} , status=status.HTTP_400_BAD_REQUEST)
        # register the job seeker
        serializer = JobSeekerSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            data['user'] = user
            # adding the city and country
            # TODO fix this
            country_data = self.country_and_city_id(request)
            if isinstance(country_data , Response):
                return country_data
            city = country_data['city']
            province = country_data['province']
            job_seeker = serializer.save(city=city , province=province)
            # assign base permission
            utils.assign_base_permissions(user, job_seeker, "jobseeker")
            return Response(data={"detail" : "Job Seeker registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(data={"errors" : serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(
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
    def patch(self , request ) :
        user = request.user
        job_seeker = utils.job_seeker_exists(user)
        if not job_seeker :
            return Response(data={"detail" : "job seeker does not exists for this user" } , status=status.HTTP_404_NOT_FOUND)

        if not user.has_perm('change_job_seeker' , job_seeker) :
            return Response(data={"detail" : "user does not have permission to do this action"} , status=status.HTTP_403_FORBIDDEN)

        serializer = JobSeekerSerializer(job_seeker , data=request.data , partial=True)
        # TODO fix the location update bug
        if serializer.is_valid():
            # country_data = self.country_and_city_id(request)
            # if isinstance(country_data , Response):
            #     return country_data
            # city = country_data['city']
            # country = country_data['country']
            # state = country_data['state']
            # serializer.save(user=user , city=city , country=country , state=state)
            serializer.save(user=user)
            return Response(data={"detail" : "job seeker updated successfully"}, status=status.HTTP_200_OK)
        return Response(data={"errors" : serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class ResumeRegister(APIView) :

    parser_classes = [MultiPartParser] 
    @swagger_auto_schema(
        operation_summary="get data resume for the job seeker",
        operation_description="get data resume for the job seeker if job seeker exists and have permission",
        responses={
            200 : ResumeSerializer,
            400 : "invalid parameters",
            404 : "job seeker was not found"
        }
    )
    def get(self , request):
        user = request.user
        # get the user
        job_seeker = utils.job_seeker_exists(user)
        if not job_seeker :
            return Response(data={"detail" : "there is no job seeker asign to this user"} , status=status.HTTP_404_NOT_FOUND)
        # finding resume base on the job_seeker
        try :
            resume = Resume.objects.get(job_seeker=job_seeker)
        # check if the resume exist
        except Resume.DoesNotExist :
            return Response(data={"detail" : "there is no resume for this job seeker"} , status=status.HTTP_404_NOT_FOUND)
        # have permission to view the resume
        if not user.has_perm('view_resume' , resume) :
            return Response(data={"detail" : "user does not have permission to view this resume"} , status=status.HTTP_403_FORBIDDEN)
        serializer = GetResumeSerializer(resume)
        return Response(data={"detail" : serializer.data}, status=status.HTTP_200_OK)
    
    
    
    @swagger_auto_schema(
        operation_summary="register resume for the job seeker",
        operation_description="register resume for the job seeker if job seeker exists",
        request_body=ResumeSerializer,
        responses={
            200 : "resume registered successfully",
            400 : "invalid parameters",
            403 : "does not have permission to do this action",
            404 : "job seeker was not found"
        }
    )
    def post(self , request) :
        user = request.user
        print(request.FILES , request.data)
        # return if job seeker does not exists
        job_seeker = utils.job_seeker_exists(user)
        if not job_seeker :
            return Response(data={"detail" : "there is no job seeker asgin to this user"} , status=status.HTTP_404_NOT_FOUND)
        # return if resume exists
        if Resume.objects.filter(job_seeker=job_seeker).exists() :
            return Response(data={"detail" : "Resume for this job seeker exist . please update it"})
        # create resume
        serializer = ResumeSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            data['job_seeker'] = job_seeker
            resume = serializer.save()
            # assign the basic permission to the user
            # its better handle this in signals cause there is security problem if we create the resume and the assign does not work
            utils.assign_base_permissions(user , resume , "resume")
            return Response(data={"detail" : "resume created successfully"}, status=status.HTTP_201_CREATED)
        return Response(data={"errors" : serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(
        operation_summary="update resume for the job seeker",
        operation_description="update resume for the job seeker if job seeker exists and have the permission",
        request_body=ResumeSerializer,
        responses={
            200 : "resume updated successfully",
            400 : "invalid parameters",
            403 : "does not have permission to do this action",
            404 : "job seeker was not found"
        }
    )
    def patch(self , request):
        user = request.user
        print(request.data)
        job_seeker = utils.job_seeker_exists(user)
        if not job_seeker :
            return Response(data={"detail" : "job seeker does not exist"} , status=status.HTTP_404_NOT_FOUND)
        try :
            resume = Resume.objects.get(job_seeker=job_seeker)
        except Resume.DoesNotExist :
            return Response(data={"detail" : "resume does not exist"} , status=status.HTTP_404_NOT_FOUND)
        if not user.has_perm('change_resume' , resume) :
            return Response(data={"detail" : "user does not have permission to change this resume"} , status=status.HTTP_403_FORBIDDEN)
        serializer = ResumeSerializer(resume, data=request.data ,partial=True)
        if serializer.is_valid() :
            serializer.save(job_seeker=job_seeker)
            return Response(data={"detail" : "resume updated successfully"} , status=status.HTTP_200_OK)
        return Response(data={"errors" : serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="delete resume for the job seeker",
        operation_description="delete resume for the job seeker if job seeker exists",
        responses={
            200 : "resume deleted successfully",
            400 : "invalid parameters",
            403 : "does not have permission to do this action",
            404 : "job seeker was not found"
        }
    )
    def delete(self , request):
        user = request.user
        job_seeker = utils.job_seeker_exists(user)
        if not job_seeker :
            return Response(data={"detail" : "job seeker does not exist"} , status=status.HTTP_404_NOT_FOUND)
        try :
            resume = Resume.objects.get(job_seeker=job_seeker)
        except Resume.DoesNotExist :
            return Response(data={"detail" : "resume does not exist"}, status=status.HTTP_404_NOT_FOUND)
        if not user.has_perm('delete_resume' , resume) :
            return Response(data={"detail" : "user does not have permission to delete resume"} , status=status.HTTP_403_FORBIDDEN)
        resume.delete()
        return Response(data={"detail" : "resume deleted successfully"} , status=status.HTTP_201_CREATED)

class ApplyForJob(APIView):

    @swagger_auto_schema(
        operation_summary="get data about that job seeker job applies",
        operation_description="get the data about job applies that job seeker has done if exists and have permission",
        responses={
            200 : ApplicationSerializer,
            400 : "invalid parameters",
            403 : "does not have permission to do this action",
            404 : "job seeker was not found"
        }
    )
    def get(self, request):
        user = request.user 
        job_seeker = utils.job_seeker_exists(user)
        if not job_seeker :
            return Response(data={"detail" : "user does not exist"} , status=status.HTTP_404_NOT_FOUND)

        applications = Application.objects.filter(job_seeker=job_seeker)
        if not applications.exists() :
            return Response(data={"detail" : "there is no job application that this user has done"} , status=status.HTTP_404_NOT_FOUND)
        # if not user.has_perm('view_application' , applications) :
        #     return Response(data={"detail" : "user does not have permission to view this job apply"} , status=status.HTTP_403_FORBIDDEN)
        serializer = ApplicationSerializer(applications, many=True)
        return Response(data={"detail" : serializer.data}, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_summary="register for job opportunity",
        operation_description="register for job opportunity if job seeker and the offer exists",
        request_body=ApplicationSerializer,
        responses={
            200 : "job application was successfull",
            400 : "invalid parameters",
            404 : "job seeker was not found"
        }
    )
    def post(self , request) :
        user = request.user
        # check that user is asign to job seeker
        job_seeker = utils.job_seeker_exists(user)
        if not job_seeker :
            return Response(data={"error" : "there is no job seeker asign to this user"} , status=status.HTTP_404_NOT_FOUND)
        offer_id  = request.data.get('offer_id') 
        if not offer_id :
            return Response(data={"error" : "offer_id must be entered"} , status=status.HTTP_400_BAD_REQUEST)
        
        

        serializer = ApplicationSerializer(data=request.data)
        
        if serializer.is_valid() :
            data = serializer.validated_data
            try :
                job_opportunity = JobOpportunity.objects.get(pk=offer_id , status="approved")
            except JobOpportunity.DoesNotExist :
                return Response(data={"error"  : "job opportunity does not exist"})
            
            apply = Application.objects.filter(job_seeker=job_seeker , job_opportunity=job_opportunity)
            
            if apply.exists() : 
                return Response(data={"error" : "job seeker applied for this job before"} , status=status.HTTP_400_BAD_REQUEST)
            
            data['job_seeker'] = job_seeker
            data['job_opportunity'] = job_opportunity
   
            application = serializer.save()
            # assign the permission to view/delete the offer later
            assign_perm('view_application' , user , application)
            assign_perm('delete_application' , user , application)
            assign_perm('view_application' , job_opportunity.employer.user , application)
            assign_perm('change_application' , job_opportunity.employer.user , application)
            return Response(data={"detail" : "job application was successfull"} , status=status.HTTP_201_CREATED)

        return Response(data={"errors" : serializer.errors} , status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_summary="delete the job apply",
        operation_description="delete the job opportunity if job seeker exists and job seeker has applied for any",
        responses={
            200 : "job application deleted successfully",
            400 : "invalid parameters",
            404 : "job seeker was not found"
        }
    )
    # wrong code
    def delete(self , request):
        user = request.user
        job_seeker = utils.job_seeker_exists(user)
        if not job_seeker :
            return Response(data={"detail" : "user does not exist"} , status=status.HTTP_404_NOT_FOUND)
        try :
            applications = Application.objects.get(job_seeker=job_seeker)
        except Application.DoesNotExist :
            return Response(data={"detail" : "there is no job application that this user has done"} , status=status.HTTP_404_NOT_FOUND)
        if not user.has_perm('delete_application' , applications) :
            return Response(data={"detail" : "user does not have permission to delete this job apply"} , status=status.HTTP_403_FORBIDDEN)
        applications.delete()
        return Response(data={"detail" : "deleted succesfully"} , status=status.HTTP_200_OK)


class AppliesForJob(APIView):
        
    @swagger_auto_schema(
        operation_summary="get the applies for a specific job offer",
        operation_description="get all the apply for the job opportunity",
        responses={
            200 : ApplicationSerializer,
            400 : "invalid parameters",
            404 : "job seeker was not found"
        }
    )
    def get(self , request) :
        job_id = request.data.get('id')
        try :
            job_opportunity = JobOpportunity.objects.get(pk=job_id)
        except JobOpportunity.DoesNotExist :
            return Response(data={"detail" : "job opportunity with this job id does not exist"} , status=status.HTTP_404_NOT_FOUND)
        applications = Application.objects.filter(job_opportunity=job_opportunity)
        if not applications.exists() :
            return Response(data={"detail" : "there is apply for this job"} , status=status.HTTP_404_NOT_FOUND)
        serializer = ApplicationSerializer(applications, many=True)
        return Response(data={"detail" : serializer.data}, status=status.HTTP_200_OK)
    

    
class JobSeekerInterviewSchedule(APIView , InterviewScheduleMixin , FilterInterviewScheduleMixin) : 
    @swagger_auto_schema(
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
    def get(self , request):
        user = request.user
        job_seeker = utils.job_seeker_exists(user)
        if not job_seeker :
            return Response(data={"error" : "employer does not exists"} ,status=status.HTTP_404_NOT_FOUND )
        # get the schedule base on employer
        interviews = InterviewSchedule.objects.filter(apply__job_seeker = job_seeker ).exclude(status__in = ["rejected_by_employer" , "rejected_by_jobseeker"])
        
        for interview in interviews :
            if not user.has_perm("view_interviewschedule",interview):
                return Response(data={"error" : "user does not have permission to do this action"} , status=status.HTTP_403_FORBIDDEN)
        
        filtered_data = self.filter_interview(interviews)
        if isinstance(filtered_data , Response) :
            return filtered_data
        
        serializer = InterviewScheduleSerializer(filtered_data , many=True)
        return Response(data={"data" : serializer.data} , status=status.HTTP_200_OK)
    
    
    
    
    @swagger_auto_schema(
        operation_summary="accept or suggest the interview time of the job apply ",
        operation_description="job seekers can accept or suggest new time instead of the employer time for the interview if employer accept the time it will be set as interview time",
        request_body=ChangeInterviewJobSeekerScheduleSerializer,
        responses={
            200 : "success",
            400 : "invalid parameters",
            403 : "does not have permission",
            404 : "employer/job apply was not found",
        },
        security=[{"Bearer" : []}]
    )
    def patch(self , request) :
        user = request.user

        job_seeker_time = request.data.get('job_seeker_time')
        apply_id = request.data.get("apply_id")
        
        apply = self.check_apply_and_permissions(apply_id , user , kind="job_seeker")
        if isinstance(apply , Response) :
            return apply
        
        interview = self.check_interview(apply)
        if isinstance(interview , Response) :
            return interview
        
        conflict = self.check_conflict(interview.pk , job_seeker_time , apply , "job_seeker")
        if isinstance(conflict , Response) :
            return conflict

        
        
        serializer = ChangeInterviewJobSeekerScheduleSerializer(interview ,data=request.data , partial=True)
        if serializer.is_valid() :  
            job_seeker_time = serializer.validated_data['job_seeker_time']
            employer_time = interview.employer_time
            if employer_time :
                if employer_time == job_seeker_time :
                    serializer.validated_data['status'] = 'approved'
                    serializer.validated_data['interview_time'] = employer_time
                if job_seeker_time != employer_time :
                    print("Test3")
                    serializer.validated_data['status'] = 'rejected_by_jobseeker'
                    
            serializer.save()
            return Response(data={"success" : True ,"data" : serializer.data ,"interview_time" :  interview.interview_time } , status=status.HTTP_200_OK)
        return Response(data={"errors" : serializer.errors} , status=status.HTTP_400_BAD_REQUEST)



        
class ParticapteTest(APIView) :
    # list of test that user participated
    def get(self , request) :
        user = request.user
        job_seeker = utils.job_seeker_exists(user) 
        if not job_seeker :
            return Response(data={"error" : "job seeker does not exists"} , status=status.HTTP_404_NOT_FOUND)
        
        try :
            resume = Resume.objects.prefetch_related("test").get(job_seeker=job_seeker)
        except :
            return Response(data={"error" : "error occured"} , status=status.HTTP_400_BAD_REQUEST)
        
        tests = resume.test.all()
        serializer = TestSerializer(tests , many=True)
        return Response(data={"data" : serializer.data} , status=status.HTTP_200_OK)
        
    def post(self , request) :
        user = request.user
        job_seeker = utils.job_seeker_exists(user) 
        if not job_seeker :
            return Response(data={"error" : "job seeker does not exists"} , status=status.HTTP_404_NOT_FOUND)
        
        test_id = request.data.get("test_id")
        if not test_id:
            return Response(data={"error" : "test_id must be entered"} , status=status.HTTP_400_BAD_REQUEST)
        
        try :
            test = Test.objects.get(pk=test_id , active=True)
        except Test.DoesNotExist :
            return Response(data={"error" : "there is test with this data"  , "fa_error" : "آزمونی با این مشخصات وجود ندارد"} , status=status.HTTP_404_NOT_FOUND)
        
        test_with_question = Test.objects.prefetch_related('questions').get(pk=test_id)
        questions = test_with_question.questions.all()
        # add test to the resume
        try :
            resume = Resume.objects.get(job_seeker=job_seeker)
        except Resume.DoesNotExist :
            return Response(data={"error" : "resume does not exists"} , status=status.HTTP_404_NOT_FOUND)
    
        resume.test.add(test)
        
        serializer = QuestionSerializer(questions , many=True)
        return Response(data={"success" : "True" , "data" : serializer.data} , status=status.HTTP_200_OK)
        
    
           
        
class Questions(APIView) : 
    """get all the test questions"""
    def get(self , request) :
        
        user = request.user
        job_seeker =  utils.job_seeker_exists(user)
        if not job_seeker:
            return Response(data={"error" : "job seeker does not exists"} , status=status.HTTP_404_NOT_FOUND)
        
        test_id = request.data.get('test_id')
        if not test_id :
            return Response(data={"error" : "test_id must be entered"} , status=status.HTTP_400_BAD_REQUEST)
        
        try :
            test = Test.objects.get(pk=test_id , active=True)
        except Test.DoesNotExist :
            return Response(data={"error" : "test does not exists"} , status=status.HTTP_404_NOT_FOUND)
        
        q = Question.objects.filter(test=test , active=True)
        if not q:
            return Response(data={"error" : "there is no quesiton for this test"} , status=status.HTTP_404_NOT_FOUND)
        
        serializer = QuestionSerializer(q , many=True)
        return Response(data={"data" : serializer.data }, status=status.HTTP_200_OK)          
        
        
class AnswerQuestion(APIView) :
    
    def get(self , request) :
        """get the answers for the question for the *user* """
        user = request.user
        job_seeker =  utils.job_seeker_exists(user)
        if not job_seeker:
            return Response(data={"error" : "job seeker does not exists"} , status=status.HTTP_400_BAD_REQUEST)
        
        question_id = request.data.get('question_id')
        if not question_id :
            return Response(data={"error" : "question_id must be entered"} , status=status.HTTP_400_BAD_REQUEST)
        
        try :
            q = Question.objects.get(pk=question_id, active=True)
        except Question.DoesNotExist :
            return Response(data={"error" : "question does not exists"} , status=status.HTTP_400_BAD_REQUEST)
        
        # just the answers that user has permission
        answers = Answer.objects.filter(question=q)
        answers_with_permission = get_objects_for_user(user , ['view_answer'] , answers , accept_global_perms=True)
        
        serializer = AnswerSerializer(answers_with_permission , many=True)
        return Response(data={"data" : serializer.data }, status=status.HTTP_200_OK)
          
    """answer the question the test that user participated"""
    def post(self , request) :
        user = request.user
        # did not use the utils to get the resume from the job seeker
        try :
            job_seeker = JobSeeker.objects.get(user=user)
            tests = job_seeker.resume.test.all()
            print(tests)
        except JobSeeker.DoesNotExist :
            return Response(data={"errpr" : "job seeker does not exists"} , status=status.HTTP_404_NOT_FOUND)

        
        question_id = request.data.get('question_id')
        if not question_id :
            return Response(data={"error" : "question_id must be entered"} , status=status.HTTP_400_BAD_REQUEST)
        # get the question that is active and published
        try :
            q = Question.objects.get(pk=question_id, active=True , test__publish = False)
            print(q)
            test = q.test
            print(test)
        except Question.DoesNotExist :
            return Response(data={"error" : "question does not exists"} , status=status.HTTP_400_BAD_REQUEST)
        # check that user has answer this question before or not
        a = Answer.objects.filter(question=q , user=user)
        if a.exists() :
            return Response(data={"error" : "you have answered this question before"} , status=status.HTTP_400_BAD_REQUEST)

        # check that user has participate the test or not
        if not test in tests :
            return Response(data={"error" : "must participate the test to answer the question"} , status=status.HTTP_400_BAD_REQUEST)
    
        # check that user has particapte the test or not 
        serializer = AnswerSerializer(data=request.data)
        if serializer.is_valid() :
            serializer.validated_data['user'] = user
            serializer.validated_data['question'] = q 
            answer = serializer.save()
            assign_perm("view_answer" , user , answer)
            assign_perm('change_answer' , user , answer)
            return Response(data={"success" : True , "data" : serializer.data} , status=status.HTTP_200_OK)
        
        return Response(data={"errors" : serializer.errors} , status=status.HTTP_400_BAD_REQUEST)
        



















        
        
