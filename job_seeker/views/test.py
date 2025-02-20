
# third party imports
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from guardian.shortcuts import assign_perm , get_objects_for_user
# local imports
from job_seeker.models import JobSeeker, Resume , Test , Question , Answer
from job_seeker.serializers import TestSerializer , QuestionSerializer , AnswerSerializer

from employer import utils
# Create your views here.
        
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
        



















        
        
