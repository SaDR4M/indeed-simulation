from django.urls import path
from . import views

urlpatterns = [
    path('register/' , views.EmployerRegister.as_view() , name="employer_register"),
    path('job-offer/' , views.JobOffer.as_view() , name="employer_job_offer"),
    path('all-job-offers/' , views.AllJobOffers.as_view() , name="employer_job_offers"),
    path('all-resumes/' , views.AllResumes.as_view() , name="all-resumes"),
    path('change-offer-status/' , views.ChangeJobOfferStatus.as_view() , name="change_offer_status"),
    path('job-applies/' , views.ResumesForOffer.as_view() , name="resume_applies"),
    path('view-resume/' , views.ResumeViewer.as_view() , name="view_resume"),
    path('change-apply-status/' , views.ChangeApplyStatus.as_view() , name="change_apply_status"),
]
    