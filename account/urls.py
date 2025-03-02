from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView , TokenRefreshView , TokenVerifyView
from account.views import UserOTPApiView , SignInApiView , SignUpApiView , SignInWithPassApiView ,  UpdateCredential , UserDataCompleteApiView

urlpatterns = [
    # path('signin/', SignIn.as_view() , name='signin_with_pass'),
    path('get-otp/' , UserOTPApiView.as_view() , name="send_otp"),
    path('signin/' , SignInApiView.as_view() , name="signin"),
    path('signup/' , SignUpApiView.as_view() , name="signup"),
    path('signin-wp/' , SignInWithPassApiView.as_view() , name="signin_with_pass"),
    path('update-credential/', UpdateCredential.as_view(), name='update_credential'),
    path('need-complete/' , UserDataCompleteApiView.as_view() , name="user_need_complete")
]
