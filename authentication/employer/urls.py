from django.urls import path
from . import views

urlpatterns = [
    path('register/' , views.EmployerRegister.as_view() , name="employer_register"),
    path('job-offer/' , views.JobOffer.as_view() , name="employer_job_offer"),
    path('all-job-offers/' , views.AllJobOffers.as_view() , name="employer_job_offers"),

]
