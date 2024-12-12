from django.urls import path

#  local imports
from . import views
urlpatterns = [
    path('register/' , views.JobSeekerRegister.as_view(), name='register_jobseeker'),
    path('resume/' , views.ResumeRegister.as_view(), name='resume_jobseeker'),
    path('apply/', views.ApplyForJob.as_view(), name="employer_aplly"),
    path('job-applies/' , views.AppliesForJob.as_view(), name="job_applies"),
    path('jobseeker-interview-schedule/' , views.JobSeekerInterviewSchedule.as_view() , name="schedule_time"),
    path('test/' , views.MangeTest.as_view() , name='test'),
    path('all-questions/' , views.Questions.as_view() , name="all_questions"),
    path('test/questions/' , views.ManageQuestion.as_view() , name="test_questions"),
    path('test/participate/' , views.ParticapteTest.as_view() , name="participate_test"),
    path('test/participate/answer/' , views.AnswerQuestion.as_view() , name="answer_participate_test"),
    #TODO ADD THIS PATH TO THE ADMIN URLS 
    path('all-jobseekers/' , views.AllJobSeekers.as_view() , name="all_jobseekers")
]