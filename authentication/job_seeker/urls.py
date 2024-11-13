from django.urls import path

#  local imports
from . import views
urlpatterns = [
    path('register/' , views.JobSeekerRegister.as_view(), name='register-job-seeker'),
    path('resume/' , views.ResumeRegister.as_view(), name='resume-job-seeker'),
    path('apply/', views.ApplyForJob.as_view(), name="employer_aplly"),
    path('job-applies/' , views.AppliesForJob.as_view(), name="job-applies"),
]