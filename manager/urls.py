from django.urls import path

from . import views

urlpatterns = [
    path('create-package/' , views.CreatePackage.as_view() , name="create-package"),
    path('all-packages/' , views.AllPackage.as_view() , name="all_packages"),
    path('test/' , views.MangeTest.as_view() , name='test'),
    path('test/questions/' , views.ManageQuestion.as_view() , name="test_questions"),
    path('all-jobseekers/' , views.AllJobSeekers.as_view() , name="all_jobseekers"),
    path('all-employers/' , views.AllEmployers.as_view() , name='all_employers'),
    path('change-offer-status/' , views.ChangeJobOfferStatus.as_view() , name="change_offer_status"),
    path('stack/' , views.TechnologyCategoryMngApiView.as_view())
]