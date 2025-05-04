from django.urls import path
from . import views

urlpatterns = [
    path('register/' , views.EmployerRegisterApiView.as_view() , name="employer_register"),
    path('update/' , views.EmployerUpdateApiView.as_view() , name="employer_update"),
    path('data/' , views.EmployerDataApiView.as_view() , name="employer_data"),
    path('job-offer/' , views.JobOffer.as_view() , name="employer_job_offer"),
    path('employer-job-offers/' , views.JobOfferList.as_view()),
    path('all-resumes/' , views.AllResumes.as_view() , name="all_resumes"),
    path('job-applies/' , views.ResumesForOffer.as_view() , name="resume_applies"),
    path('view-resume/' , views.ResumeViewer.as_view() , name="view_resume"),
    path('view-apply-resume/' , views.AppliedResumeViewer.as_view() , name='view_apply_resume'),
    path('change-apply-status/' , views.ChangeApplyStatus.as_view() , name="change_apply_status"),
    path('employer-interview-schedule/' , views.EmployerInterviewSchedule.as_view() , name="schedule_time"),
]
    
    
    