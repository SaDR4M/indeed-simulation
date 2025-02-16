from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView , TokenRefreshView , TokenVerifyView
from account.views import UserOTPApiView , SignInApiView , SignUpApiView , UpdateCredential

urlpatterns = [
    # path('signin/', SignIn.as_view() , name='signin_with_pass'),
    path('update-credential/', UpdateCredential.as_view(), name='update_credential'),
    path('get_otp/' , UserOTPApiView.as_view() , name="send_otp"),
    path('signin/' , SignInApiView.as_view() , name="signin"),
    path('signup/' , SignUpApiView.as_view() , name="signup"),
]
