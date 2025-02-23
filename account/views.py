# built-in imports
import re
import uuid
# django & rest imports
from django.contrib.auth.hashers import make_password
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
# third party imports
from icecream import ic
# local imports
from account.models import User
from account.utils import  (signin_user ,
                            signup_user ,
                            check_otp ,
                            signin_user_wp ,
                            update_user_password,
                            validate_user_mobile,
                            create_otp
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
        # validate user mobile
        mobile = request.data.get("mobile")
        validated_mobile = validate_user_mobile(mobile)
        if isinstance(validate_user_mobile , Response) :
            return validated_mobile
    
        with_call = False
        if request.data.get("with_call") == 'true':
            with_call = True      

        # create otp
        otp = create_otp(mobile)
        if isinstance(otp , Response) :
            return otp
        
        # TODO Security: Dont send code in response
        req = {
            "succeeded": True,
            "mobile": mobile,
            "code" : otp,
        }  

        # call for the OTP
        if with_call == True:
            req.update({
                "send_with" : "CALL"
                })
            make_call(
                receptor = mobile,
                message = otp,
            )
        # send message for OTP
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
        # TODO remove code from response
        user_exists = User.objects.filter(mobile=mobile).exists()
        req.update({
            "user_exists" : user_exists,
            "send_otp": True,
            "remain_time": 60,
        })
        ic(req)
        # save OTP
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
        otp = request.data.get("otp")
        role = request.data.get("role")
        is_otp_correct = check_otp(mobile , otp)
        # if otp is not correct return response
        if isinstance(is_otp_correct , Response) :
            return is_otp_correct
        try :
            user = User.objects.get(
                mobile = mobile,
                role = role
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
        role = request.data.get("role")
        password = request.data.get('password')
        # check if the user mobile or password were entered or not
        if not mobile and not password :
            return Response(data={"detail" : "mobile number and password are missing"} , status=status.HTTP_400_BAD_REQUEST)
        if mobile is None:
            return Response(data={"detail" : "mobile number is missing"} , status=status.HTTP_400_BAD_REQUEST)
        if password is None:
               return Response(data={"detail" : "password is missing"} , status=status.HTTP_400_BAD_REQUEST)

        sign_in = signin_user_wp(mobile , role , password , request)
        if isinstance(sign_in , Response) :
            return sign_in
        return Response(status=HTTP_500_INTERNAL_SERVER_ERROR)




# add/update credentials info
class UpdateCredential(APIView) :
    """Update user password"""
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
 







