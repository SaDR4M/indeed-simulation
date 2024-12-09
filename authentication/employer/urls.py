from django.urls import path
from . import views

urlpatterns = [
    path('register/' , views.EmployerRegister.as_view() , name="employer_register"),
    path('all-employers/' , views.AllEmployers.as_view() , name='all_employers'),
    path('job-offer/' , views.JobOffer.as_view() , name="employer_job_offer"),
    path('all-job-offers/' , views.AllJobOffers.as_view() , name="employer_job_offers"),
    path('all-resumes/' , views.AllResumes.as_view() , name="all_resumes"),
    path('change-offer-status/' , views.ChangeJobOfferStatus.as_view() , name="change_offer_status"),
    path('change-package-price/' , views.ChangePackagePrice.as_view() , name="change_package_price"),
    path('job-applies/' , views.ResumesForOffer.as_view() , name="resume_applies"),
    path('view-resume/' , views.ResumeViewer.as_view() , name="view_resume"),
    path('change-apply-status/' , views.ChangeApplyStatus.as_view() , name="change_apply_status"),
    path('employer-interview-schedule/' , views.EmployerInterviewSchedule.as_view() , name="schedule_time"),
    path('cart/' , views.Cart.as_view() , name="cart"),
    path('cart-items/' , views.Cartitems.as_view() , name="cart_items"),
    path('order/' , views.Order.as_view() , name="order"),
    path('order-items/' , views.OrderItem.as_view() , name="order_items"),
]
    
    
    