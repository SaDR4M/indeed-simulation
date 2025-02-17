# built-in imports
import re
import uuid
# django & rest imports
from django.contrib.auth.hashers import make_password , check_password
from django.core.cache import cache
from django.contrib.auth.hashers import make_password
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.status import HTTP_200_OK , HTTP_400_BAD_REQUEST , HTTP_404_NOT_FOUND , HTTP_500_INTERNAL_SERVER_ERROR
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated , AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.validators import ValidationError as rest_validation_error
# third party imports
from icecream import ic
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.tokens import RefreshToken
# local imports
from account.models import User
from account.utils import  (signin_user ,
                            signup_user ,
                            check_otp ,
                            signin_user_wp ,
                            update_user_password,
                            )
from notifications.models import SmsCategory
from core.send_sms import send_sms
from core.make_call import make_call
from account.docs import sign_in_otp_document , sign_up_document, sign_in_pass_document , update_credential_document , otp_document



class UserOTPApiView(APIView):
    """ 
    only check OTP with mobile number
    /otp_checker/
    """
    permission_classes = [AllowAny]
    @otp_document
    def post(self, request):
        '''
        send OTP to the user with SMS or CALL
        save the OTP has hash
        '''
        # filtering user
        mobile = request.data.get("mobile")
        mobile_validate = re.search("^(0|0098|98|\+98)9(0[1-5]|[1 3]\d|2[0-2]|9[1 8 9])\d{7}$", mobile)
        if not mobile_validate:
            response_json = {
                'succeeded': False,
                'show': True,
                'en_detail': 'Mobile is not correct',
                'fa_detail': 'ساختار شماره تلفن همراه نادرست است',
            }
            return Response(response_json, status=HTTP_400_BAD_REQUEST)
        with_call = False
        if request.data.get("with_call") == 'true':
            with_call = True      
        # create otp code
        otp = str(uuid.uuid4().int)[:5]
        # TODO Security: Dont send code in response
        req = {
            "mobile": mobile,
            "code" : otp,
        }  

        req.update({
            "succeeded": True,
        })
        
        key = f'OTP:{mobile}'
        if cache.get(key):  # pass the sms code sending if we already have send an sms to user
            return Response({
                "succeeded": False,
                "remain_time": cache.ttl(key),
                }, status=HTTP_200_OK)
            
        if with_call == True:
            req.update({
                "send_with" : "CALL"
                })
            make_call(
                request.data.get("mobile"),
                message = otp,
            )
        else:
            # NOTE create sms category objects otherwise it will cause an error
            # FIXME fix this
            # sms_category_obj = SmsCategory.objects.filter(code=1).first()
            
            # if sms_category_obj.isActive == True:
            #     sms_text = sms_category_obj.smsText.format(otp,otp)
            #     send_sms(
            #         request.data.get("mobile"),
            #         sms_text,
            #         sms_category_obj.id,
            #         sms_category_obj.get_sendByNumber_display(),
            #         request.user.id,
            #     )
            req.update({
                "send_with": 'SMS',
                })
        ## TODO remove code from response
        user_exists = User.objects.filter(mobile=mobile).exists()
        req.update({
            "succeeded": True,
            "user_exists" : user_exists,
            "send_otp": True,
            "remain_time": 60,
        })
        ic(req)
        hashed_otp =  make_password(otp)
        cache.set(f'OTP:{mobile}', hashed_otp, 60)
        return Response(req, status=HTTP_200_OK)
    
    
    
class SignInApiView(APIView):
    """ 
    authentication view class for normal user , Login and signup
    """
    permission_classes = [AllowAny]
    @sign_in_otp_document
    def post(self,request):
        ''' login/sign up'''
        mobile = request.data.get("mobile")
        otp = request.data.get('otp')
        is_otp_correct = check_otp(mobile , otp)
        # if otp is not correct return response
        if isinstance(is_otp_correct , Response) :
            return is_otp_correct
        # user = User.objects.get(
        #         mobile = mobile
        #     )
        try :
            user = User.objects.get(
                mobile = mobile
            )
        except User.DoesNotExist :
            return Response(
                data = {"en_detail" : "user does not exist" , "fa_detail" : "کاربر وجود ندارد"},
                status=HTTP_404_NOT_FOUND
            )
        # sign in the user
        response = signin_user(request , user)
        
        # delete OTP cache if it is not expired yet
        if cache.get(f"OTP:{mobile}") : 
            cache.delete(f"OTP:{mobile}")
            
        return response                






class SignUpApiView(APIView):
    """ 
    authentication view class for normal user , Login and signup
    """
    permission_classes = [AllowAny]
    @sign_up_document
    def post(self,request):
        ''' login/sign up'''
        mobile = request.data.get("mobile")
        otp = request.data.get('otp')
        is_otp_correct = check_otp(mobile , otp)
        # if otp is not correct return response
        if isinstance(is_otp_correct , Response) :
            return is_otp_correct
        
        # sign up the user
        response = signup_user(request)
        
        # delete OTP cache if it is not expired yet
        if cache.get(f"OTP:{mobile}") : 
            cache.delete(f"OTP:{mobile}")
            
        return response                




# sign in the user with password
class SignInWithPassApiView(APIView):
    """
    authenticate user with mobile number and the password
    3 situations may occur
    1) mobile or password is wrong
    2) password is not set
    3) user does not exists
    """
    # permission_classes = [IsAdminUser]
    permission_classes = [AllowAny]
    @sign_in_pass_document
    def post(self , request):

        mobile = request.data.get("mobile")
        password = request.data.get('password')
        # check if the user mobile or password were entered or not
        if not mobile and not password :
            return Response(data={"detail" : "mobile number and password are missing"} , status=status.HTTP_400_BAD_REQUEST)
        if mobile is None:
            return Response(data={"detail" : "mobile number is missing"} , status=status.HTTP_400_BAD_REQUEST)
        if password is None:
               return Response(data={"detail" : "password is missing"} , status=status.HTTP_400_BAD_REQUEST)

        sign_in = signin_user_wp(mobile , password , request)
        if isinstance(sign_in , Response) :
            return sign_in
        return Response(status=HTTP_500_INTERNAL_SERVER_ERROR)




# add/update credentials info
class UpdateCredential(APIView) :
    
    permission_classes = [IsAuthenticated]
    @update_credential_document
    def patch(self , request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')       
         
        updated_pass = update_user_password(user , old_password , new_password , confirm_password)
        if isinstance(updated_pass , Response) :
            return updated_pass
        return Response(status=HTTP_500_INTERNAL_SERVER_ERROR)
 







