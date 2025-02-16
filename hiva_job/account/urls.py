from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView , TokenRefreshView , TokenVerifyView
from . import views

urlpatterns = [
    path('data' , views.ShowData.as_view()),
    path('signin', views.SignIn.as_view() , name='signin'),
    path('update-credential', views.UpdateCredential.as_view(), name='update_credential'),
    path('get-otp' , views.GetOtp.as_view(), name='get_otp'),
    path('verify-otp' , views.VerifyOtp.as_view(), name='verify_otp'),
    path('token', TokenObtainPairView.as_view(), name='token'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify', TokenVerifyView.as_view(), name='token_verify'),
]
