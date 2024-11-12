from django.urls import path
from . import views

urlpatterns = [
    path('employer-register' , views.EmployerRegister.as_view() , name="employer_register")
]
