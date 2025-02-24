
import datetime
# third party imports
from django.shortcuts import render
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import status
from rest_framework.response import Response

# local imports
from package.mixins import FilterPackageMixin
from package.serializers import GetPackageSerializer , PackageSerializer
from package.models import Package

from .serializer import GetEmployerSerializer
from . import utils

from job_seeker.mixins import FilterTestMixin , FilterQuestionMixin , JobSeekerFilterMixin
from job_seeker.models import Test , Question 
from job_seeker.serializers import TestSerializer , QuestionSerializer , JobSeekerDataSerialzier

from employer.models import JobOpportunity
from employer.serializers import JobOpportunitySerializer
from employer.mixins import FilterEmployerMixin

from guardian.shortcuts import get_objects_for_user , assign_perm
# Create your views here.

# PACKAGES

# only admins can create package for job offers

class CreatePackage(APIView) :
    
    @swagger_auto_schema(
        operation_summary="create payment",
        operation_description="create payment",
        responses={
            200 : PackageSerializer,
            400 : "invalid parameters",
            404 : "job seeker was not found"
        }
    )
    def get(self , request) :
        user = request.user
        if not user.is_superuser :
            return Response(data={"detail" : "user does not have permission to do this action"} , status=status.HTTP_403_FORBIDDEN)
        packages = Package.objects.filter(user=user)
        if not packages.exists() :
            return Response(data={"detail" : "there is no package for this admin"} , status=status.HTTP_404_NOT_FOUND)
        serializer = PackageSerializer(packages , many=True)
        return Response(data={"detail" : serializer.data} , status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="create package",
        operation_description="admins create package",
        request_body=PackageSerializer,
        responses={
            200 : "package created succesfsully",
            400 : "invalid parameters",
            404 : "job seeker was not found"
        }
    ) 
    def post(self , request) :
        user = request.user
        if not user.is_superuser :
            return Response(data={"detail" : "user does not have permission to do this action"} ,status=status.HTTP_403_FORBIDDEN)
        serializer = PackageSerializer(data=request.data)
        if serializer.is_valid() :
            count = serializer.validated_data['count']
            package_type  = serializer.validated_data['type']
            price = serializer.validated_data['price']

            if price <= 0 :
                return Response(data={"error" : "price must be more than 0 "} , status=status.HTTP_400_BAD_REQUEST) 
            
            if count <= 0 :
                return Response(data={"error" : "count must be more than 1"} , status=status.HTTP_400_BAD_REQUEST)
            
            
            if package_type == "resume" :
                priority = "normal"
            else :
                priority = serializer.validated_data['priority']
            package = Package.objects.filter(type=package_type, priority=priority, count=count, active=True).count()
            if package >= 1:
                return Response(data={"detail" : "with this count you can only have on active package , deactive the other packages to register this package"} , status=status.HTTP_400_BAD_REQUEST)
            serializer.save(user=user)
            return Response(data={"detail" : "Package created successfully"} , status=status.HTTP_201_CREATED)
        return Response(data={"errors" : serializer.errors } , status=status.HTTP_400_BAD_REQUEST)
    
    
    @swagger_auto_schema(
        operation_summary="delete package",
        operation_description="admins virtual delete the package if there is a package",
        responses={
            200 : "package deeleted successfully",
            400 : "invalid parameters",
            404 : "job seeker was not found"
        }
    )
    def delete(self , request) :
        user = request.user
        package_id = request.data.get('package_id')
        if not package_id :
            return Response(data={"detail" : "package_id must be entered"} , status=status.HTTP_400_BAD_REQUEST)
        
        if not user.is_superuser :
            return Response(data={"detail" : "user does not have permission to do this action"} , status=status.HTTP_403_FORBIDDEN)
        package = Package.objects.filter(pk=int(package_id))
        
        if not package.exists() :
            return Response(data={"detail" : "package does not exist"} , status=status.HTTP_404_NOT_FOUND)
        
        package.update(active=False , deleted_at = datetime.datetime.now())
        return Response(data={"detail" : "package deleted successfully"} , status=status.HTTP_200_OK)
    
class AllPackage(APIView , FilterPackageMixin) :
    @swagger_auto_schema(
    operation_summary="all packages",
    operation_description="get all packages with filtering that . filtering option are specified in the query params document",
    manual_parameters=[
        openapi.Parameter(name="price" , in_=openapi.IN_QUERY , type=openapi.TYPE_NUMBER , description="get the packages with this EXACT price (for having range price you must define max and min price together)"),
        openapi.Parameter(name="min_price" , in_=openapi.IN_QUERY , type=openapi.TYPE_NUMBER , description="get the packages with MIN price (lte)"),
        openapi.Parameter(name="max_price" , in_=openapi.IN_QUERY , type=openapi.TYPE_NUMBER , description="get the packages with MAX price (gte)"),
        openapi.Parameter(name="active" , in_=openapi.IN_QUERY , type=openapi.TYPE_BOOLEAN , description="get the packages with EXACT type . options are True , False"),
        openapi.Parameter(name="count" , in_=openapi.IN_QUERY , type=openapi.TYPE_INTEGER , description="get the packages with EXACT count"),
        openapi.Parameter(name="type" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the packages with EXACT type. options are : 'offer' , 'resume' "),
        openapi.Parameter(name="priority" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the packages with EXACT priority. options are : 'normal' , 'urgent' "),
        openapi.Parameter(name="created_at" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING, description="get the packages with this EXACT created date time (for having range date time you must define max and min created date time together)"),
        openapi.Parameter(name="min_created_at" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the packages with MIN created date time (lte)"),
        openapi.Parameter(name="max_created_at" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the packages with MAX created date time  (gte)"),
        openapi.Parameter(name="deleted_at" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING, description="get the packages with this EXACT deleted date time (for having range date time you must define max and min deleted date time together)"),
        openapi.Parameter(name="min_deleted_at" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the packages with MIN deleted date time (lte)"),
        openapi.Parameter(name="max_deleted_at" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the packages with MAX deleted date time  (gte)"),
    ],
    responses={
            200 : GetPackageSerializer,
            400 : "invalid parameters",
            404 : "employer/offer was not found",
        },
    security=[{"Bearer" : []}]
    )
    def get(self , request) :
        user = request.user 
        if not user.is_superuser :
            return Response(data={"error" : "user does not have permission to do this action"} , status=status.HTTP_403_FORBIDDEN)
        
        packages = Package.objects.all()
        filtered_package = self.filter_package(packages , "package")
        if isinstance(filtered_package , Response) :
            return filtered_package
        
        # paginate the data
        paginator = LimitOffsetPagination()
        paginator.paginate_queryset(filtered_package , request)
        
        serializer = GetPackageSerializer(filtered_package , many=True)
        return Response(data={"data" : serializer.data} , status=status.HTTP_200_OK)
    



# TEST AND QUESTIONS


# TODO refactor the code

class MangeTest(APIView , FilterTestMixin) :
    """get the list of test with filtering"""
    @swagger_auto_schema(
        operation_summary="get the list of tests",
        operation_description="get the list of test with filtering",
        manual_parameters=[
            openapi.Parameter(name='title' , type=openapi.TYPE_STRING , in_=openapi.IN_QUERY , description="get the tests that CONTAINS this title"),
            openapi.Parameter(name='kind' , type=openapi.TYPE_STRING , in_=openapi.IN_QUERY , description="get the tests that EXACT this title"),
            openapi.Parameter(name='count' , type=openapi.TYPE_INTEGER , in_=openapi.IN_QUERY , description="get the tests that EXACT this count"),
            openapi.Parameter(name='min_count' , type=openapi.TYPE_STRING , in_=openapi.IN_QUERY , description="get the tests that MIN this count"),
            openapi.Parameter(name='max_count' , type=openapi.TYPE_STRING , in_=openapi.IN_QUERY , description="get the tests that MAX this count"),
            openapi.Parameter(name="created_at" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING, description="get the tests with EXACT created_at date"),
            openapi.Parameter(name="min_created_at" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the tests with MIN created_at date"),
            openapi.Parameter(name="max_created_at" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the tests with MAX created_at date"),
            openapi.Parameter(name="deleted_at" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING, description="get the tests with EXACT deleted_at date"),
            openapi.Parameter(name="min_deleted_at" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the tests with MIN deleted_at date"),
            openapi.Parameter(name="max_deleted_at" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the tests with MAX deleted_at date"),
        ],
        responses={
            200 : "successful",
            400 : "invalid paramters",
            403 : "user does not have permission"
        }
    )
    def get(self , request) :
        user = request.user
        if not user.is_superuser :
            return Response(data={"error" : "user does not have permission to do this action"} , status=status.HTTP_403_FORBIDDEN)
        
        # get all test that user have permission on it to view it
        tests = Test.objects.all()
        tests_permission = get_objects_for_user(user , ['view_test'] , tests , accept_global_perms=True)
        
        filtered_data = self.filter_test(tests_permission)
        if isinstance(filtered_data , Response):
            return filtered_data
        
        serializer = TestSerializer(filtered_data , many=True)
        
        return Response(data={"success" : True , "data" : serializer.data} , status=status.HTTP_200_OK)
    
    
    def post(self , request) :
        user = request.user
        if not user.is_superuser :
            return Response(data={"error" : 'user does not have permission to do this action'} , status=status.HTTP_403_FORBIDDEN)
        
        serializer = TestSerializer(data=request.data)
        
        if serializer.is_valid() :
            data = serializer.validated_data
            data['user'] = user
            kind = data['kind']
            title = data['title']
            # check that if there is active package with the same kind and name
            active_test = Test.objects.filter(kind=kind , title=title , active=True)
            if active_test.exists() :
                return Response(data={"error" : "there is active test with this name and kind" , "fa_error" : "آزمونی با این نام و نوع وجود دارد"} , status=status.HTTP_400_BAD_REQUEST )
            test = serializer.save() 
            # assigning permission to the user
            assign_perm("view_test" , user , test)
            assign_perm("change_test" , user , test)
            assign_perm("delete_test" , user , test)
            return Response(data={"success" : True , "data" : serializer.data})    
        return Response(data={"errors" : serializer.errors} , status=status.HTTP_400_BAD_REQUEST)
    
    
    def patch(self , request) :
        user = request.user
        if not user.is_superuser :
            return Response(data={"error" : 'user does not have permission to do this action'} , status=status.HTTP_403_FORBIDDEN)

        test_id = request.data.get('test_id')
        if not test_id :
            return Response(data={"error" : "test_id must be entered"} , status=status.HTTP_400_BAD_REQUEST)
        
        try :
            test = Test.objects.get(pk=test_id , active=True)
        except Test.DoesNotExist :
            return Response(data={"error" : "test does not exists"} , status=status.HTTP_404_NOT_FOUND)  
        
        if user.has_perm("change_test" , test) :
            return Response(data={"error" : "user does not have permission to do this action"} , status=status.HTTP_403_FORBIDDEN) 
        
        serializer = TestSerializer(test , data=request.data , partial=True)
        if serializer.is_valid() :
            serializer.validated_data['user'] = user
            publish = serializer.validated_data['publish']
            if publish == True :
                can_publish = utils.can_publish(test)
                if not can_publish :
                     return Response(data={"error" : "the test can not be published due the count of question user entered"} , status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(data={"success" : True , "data" : serializer.data} ,  status=status.HTTP_200_OK)
        return Response(data={"errors" : serializer.errors} , status=status.HTTP_400_BAD_REQUEST)            
            
    def delete(self , request) :
        user = request.user
        if not user.is_superuser :
            return Response(data={"error" : 'user does not have permission to do this action'} , status=status.HTTP_403_FORBIDDEN)
        
        test_id = request.data.get('test_id')
        if not test_id :
            return Response(data={"error" : "test_id must be entered"} , status=status.HTTP_400_BAD_REQUEST)
        # check if there active test exists or not
        try :
            test = Test.objects.get(pk=test_id , active=True)
        except Test.DoesNotExist :
            return Response(data={"error" : "test does not exists" , "fa_error" : "آزمونی با این اطلاعات وجود ندارد"} , status=status.HTTP_404_NOT_FOUND)
        
        if user.has_perm("delete_test" , test) :
            return Response(data={"error" : "user does not have permission to do this action"} , status=status.HTTP_403_FORBIDDEN)
        # virtual delete the test
        test.deleted_at = datetime.datetime.now()
        test.active = False
        test.save()
        return Response(data={"success" : True } , status=status.HTTP_200_OK)
    
    
    
    
class ManageQuestion(APIView , FilterQuestionMixin) :
    """get list of test question"""
    @swagger_auto_schema(
        operation_summary="get the list of tests",
        operation_description="get the list of test with filtering",
        manual_parameters=[
            openapi.Parameter(name='question' , type=openapi.TYPE_STRING , in_=openapi.IN_QUERY , description="get the questions that CONTAINS this question(it means the question TEXT)"),
            openapi.Parameter(name='answer' , type=openapi.TYPE_STRING , in_=openapi.IN_QUERY , description="get the questions that CONTAINS this answer"),
            openapi.Parameter(name='score' , type=openapi.TYPE_INTEGER , in_=openapi.IN_QUERY , description="get the questions with this EXACT this score"),
            openapi.Parameter(name='min_score' , type=openapi.TYPE_STRING , in_=openapi.IN_QUERY , description="get the questions that MIN this min_score"),
            openapi.Parameter(name='max_score' , type=openapi.TYPE_STRING , in_=openapi.IN_QUERY , description="get the questions that MAX this max_score"),
            openapi.Parameter(name="created_at" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING, description="get the questions with EXACT created_at date"),
            openapi.Parameter(name="min_created_at" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the questions with MIN created_at date"),
            openapi.Parameter(name="max_created_at" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the questions with MAX created_at date"),
            openapi.Parameter(name="deleted_at" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING, description="get the questions with EXACT deleted_at date"),
            openapi.Parameter(name="min_deleted_at" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the questions with MIN deleted_at date"),
            openapi.Parameter(name="max_deleted_at" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the questions with MAX deleted_at date"),
        ],
        responses={
            200 : "successful",
            400 : "invalid paramters",
            403 : "user does not have permission"
        }
    )
    def get(self , request) :
        """get the list of all questions with filter . for user to see all the questions like question bank"""
        user = request.user
        test_id = request.data.get('test_id')
    
        
        if not user.is_superuser :
            return Response(data={"error" : 'user does not have permission to do this action'} , status=status.HTTP_403_FORBIDDEN)

        q = Question.objects.filter(active=True)
        
        filtered_data = self.filter_question(q)
        if isinstance(filtered_data , Response) :
            return filtered_data
        # if not qa :
        #     return Response(data={"data" : {}} , status=status)
        
        serializer = QuestionSerializer(filtered_data , many=True)
        return Response(data={"data" : serializer.data} , status=status.HTTP_200_OK)
    
    # add new question to the test
    def post(self , request) :
        """create questions for tests"""
        user = request.user
        if not user.is_superuser :
            return Response(data={"error" : 'user does not have permission to do this action'} , status=status.HTTP_403_FORBIDDEN)
        
        test_id = request.data.get("test_id")
        if not test_id :
            return Response(data={"error" : "test_id must be entered" } , status=status.HTTP_400_BAD_REQUEST)
            
        try :
            test = Test.objects.get(pk=test_id , active=True)
        except Test.DoesNotExist :
            return Response(data={"error" : "there is test with this data"  , "fa_error" : "آزمونی با این مشخصات وجود ندارد"} , status=status.HTTP_404_NOT_FOUND)


        serializer = QuestionSerializer(data=request.data)
        if serializer.is_valid() :
            serializer.validated_data['test'] = test   
            serializer.validated_data['user'] = user
            question = serializer.validated_data['question']
            
            q = Question.objects.filter(question__icontains=question  , active=True)
            if q.exists() :
                return Response(data={"error" : "there is active question"}  , status=status.HTTP_400_BAD_REQUEST)

            q = serializer.save()

            assign_perm("view_question" , user , q)
            assign_perm("change_question" , user , q)
            assign_perm("delete_question" , user , q)
                    
            return Response(data={"success" : True , "data" : serializer.data})
        return Response(data={"errors" :serializer.errors} , status=status.HTTP_400_BAD_REQUEST)
        
        
        
    
    def patch(self , request) :
        user = request.user
        if not user.is_superuser :
            return Response(data={"error" : 'user does not have permission to do this action'} , status=status.HTTP_403_FORBIDDEN)
            
        question_id = request.data.get("question_id")
        
        if not question_id :
            return Response(data={"error" : "question_id must be entered" } , status=status.HTTP_400_BAD_REQUEST)

        try :
            q = Question.objects.get(pk=question_id , active=True ,  )
        except Question.DoesNotExist :
            return Response(data={"error" : "there is question with this data"  , "fa_error" : "سوالی با این مشخصات وجود ندارد"} , status=status.HTTP_404_NOT_FOUND)
    
        if user.has_perm("change_question" , q) :
            return Response(dat={"error" : "user does not have permission to do this action"} , status=status.HTTP_403_FORBIDDEN)

        
        
        serializer = QuestionSerializer(q , data=request.data , partial=True)
        if serializer.is_valid :
            serializer.validated_data['test'] = q.test
            serializer.save()

            return Response(data={"success" : True} , status=status.HTTP_200_OK)
        return Response(data={"errors" : serializer.errors} , status=status.HTTP_400_BAD_REQUEST)
    
    
    
    def delete(self , request) :
        user = request.user
        if not user.is_superuser :
            return Response(data={"error" : 'user does not have permission to do this action'} , status=status.HTTP_403_FORBIDDEN)
            
        question_id = request.data.get("question_id")
        
        if not question_id :
            return Response(data={"error" : "question_id must be entered" } , status=status.HTTP_400_BAD_REQUEST)
          
        try :
            q = Question.objects.get(pk=question_id , active=True )
        except Question.DoesNotExist :
            return Response(data={"error" : "there is question with this data"  , "fa_error" : "سوالی با این مشخصات وجود ندارد"} , status=status.HTTP_404_NOT_FOUND)

        if user.has_perm("delete_question" , q) :
            return Response(dat={"error" : "user does not have permission to do this action"} , status=status.HTTP_403_FORBIDDEN)
        
        q.deleted_at = datetime.datetime.now()
        q.active = False
        q.save()
        return Response(data={"success" : True} , status=status.HTTP_200_OK)
        



# JOB SEEKERS

class AllJobSeekers(APIView , JobSeekerFilterMixin) :
    
    def get(self , request) :
        user = request.user
        if not user.is_superuser :
            return Response(data={"error" : "user does not have permission to do this action"} , status=status.HTTP_403_FORBIDDEN) 
        
        filtered_jobseekers = self.filter_jobseeker()       
        if isinstance(filtered_jobseekers , Response) :
            return filtered_jobseekers   

        # paginate the dataA
        paginator = LimitOffsetPagination()
        paginator.paginate_queryset(filtered_jobseekers , request)
        
        serializer = JobSeekerDataSerialzier(filtered_jobseekers , many=True)
        return Response(data={"data" : serializer.data} , status=status.HTTP_200_OK)


# EMPLOYERS 

class ChangeJobOfferStatus(APIView) :
    @swagger_auto_schema(
        operation_id="change job offer status",
        operation_summary="change the job opportunity status",
        operation_description="only admins can change the job opportunity status",
        request_body=JobOpportunitySerializer,
        responses={
            200 : JobOpportunitySerializer,
            400 : "invalid parameters",
            404 : "employer/offer was not found",
        },
        security=[{"Bearer" : []}]
    )
    def patch(self , request) :
        user = request.user
        offer_id = request.data.get('offer_id')
        status = request.data.get('status')
        # only admins can change the offer status
        if not user.is_superuser :
            return Response(data={"detail" : "user does not have permission to do this action"} , status=status.HTTP_403_FORBIDDEN) 
             
        if not offer_id :
            return Response(data={"detail" : "offer_id must be enter"} , status=status.HTTP_400_BAD_REQUEST)
        
        if not status :
            return Response(data={"detail" : "status must be enter" , "success" : False} , status=status.HTTP_400_BAD_REQUEST)
        
        job_opportunity = JobOpportunity.objects.filter(pk=offer_id)
        if not job_opportunity.exists() :
            return Response(data={"detail" : "there is no job opportunity with this information"} , status=status.HTTP_404_NOT_FOUND)
        
        
        serializer = JobOpportunitySerializer(job_opportunity.first() , data=request.data , partial=True)
        if serializer.is_valid() :
            data = serializer.validated_data
            status = data['status']
            # change the active to true if the offer is approved by the admin
            if status == "approved" :
                data['active'] = True
            serializer.save()
            return Response(data={"success" : True , "data" : serializer.data} , status=status.HTTP_200_OK)
        return Response(data={"success" : False , "errors" : serializer.errors} , status=status.HTTP_200_OK)

# admins change the price of the package
# the package will be deleted and then with that package info and new price a new package will be created
class ChangePackagePrice(APIView) :
    def post(self , request):
        user = request.user
        package_id = request.data.get('package_id')
        new_price = request.data.get('new_price')
        if not new_price :
            return Response(data={"detail" : "new price must be enetered"} , status=status.HTTP_400_BAD_REQUEST)
        if not package_id :
            return Response(data={"detail" : "package_id must be entered"} , status=status.HTTP_400_BAD_REQUEST)
        if not user.is_superuser :
            return Response(data={"detail" : "user does no have permission to do this action"} , status=status.HTTP_403_FORBIDDEN)
        try :
            package = Package.objects.get(pk = package_id)
        except Package.DoesNotExist :
            return Response(data={"detail" : "package does not exists"} , status=status.HTTP_404_NOT_FOUND)
        package_data = PackageSerializer(package).data
        package_data['price'] = new_price
        package.active = False
        package.save()
        serializer = PackageSerializer(data=package_data)
        if serializer.is_valid() :
            serializer.save(user=user , active=True)
            return Response(data={"detail" : "success"} , status=status.HTTP_200_OK)
        return Response(data={"success" : False , "errors" : serializer.errors} , status=status.HTTP_400_BAD_REQUEST)
    
    
class AllEmployers(APIView , FilterEmployerMixin) :
    def get(self , request) :
        """get all the employer with some filtering"""
        user = request.user
        if not user.is_superuser :
            return Response(data={"error" : "User does not have permission to do this action"}  , status=status.HTTP_403_FORBIDDEN)
        
        employer = self.filter_employer()
        # return the response if there was any problem
        if isinstance(employer , Response) :
            return employer
        
        # paginate the result
        paginator = LimitOffsetPagination()
        paginator.paginate_queryset(employer , request)
        
        serializer = GetEmployerSerializer(employer , many=True)
        return Response(data={"data" : serializer.data} , status=status.HTTP_200_OK)
