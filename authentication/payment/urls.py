from django.urls import path
# local imports
from . import views
urlpatterns = [
    path('create-payment' , views.CreatePayment.as_view() , name="create-payment")
]