# built-in
import requests
import datetime
from user_agents import parse
import random
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# django & rest imports
from django.core.cache import cache
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.contrib.auth.hashers import check_password
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.status import HTTP_200_OK , HTTP_400_BAD_REQUEST
from django.core.cache import cache
# third party
# local imports
from account.models import UserLog
from account.serializer import UserSerializer
from core.ems import validation_error
from account.models import User , Message
from account import tasks



# for gurdian Anonymous user
def get_anonymous_user(User) : 
    anonymous_user , created = User.objects.get_or_create(
        id = 9999999999,
        defaults={
            "username" : "9999999999",
            "mobile" : "9999999999",
            "role" : 1
        }
    )
    if anonymous_user :
        return anonymous_user
    else :
        return created
    
    
def create_user_log(user_obj, request, kind):
    ''' based on the action (login, wrong pass and ...) we create a log for user and save the ip address and user agent info'''
    
    user_agent = request.headers.get("User-Agent")
    user_agent_spilited = parse(user_agent)
    browser = f"by browser {user_agent_spilited.browser.family} / version {user_agent_spilited.browser.version_string}"
    os = f"by os {user_agent_spilited.os.family} / version {user_agent_spilited.os.version_string}"
    device = f"by device {user_agent_spilited.device.family} /brand {user_agent_spilited.device.brand} model {user_agent_spilited.device.model}"
    for_admin = str(user_agent_spilited)
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")

    user_log = UserLog.objects.create(
        log_kind=kind,  # Wrong Password
        browser=browser,
        os=os,
        device=device,
        ip_address=ip,
        for_admin=for_admin,
        user=user_obj,
    )
    user_log.save()
    
    
def check_user_birthday(user) :
        today = datetime.date.today()
        today_is_birthday = False
        # set year to 1 check the month an day
        a = user.birthday.replace(year=1)
        b = today.replace(year=1)
        if user.last_login:
            last_login = user.last_login.date()
            if last_login < today and  a == b:
                today_is_birthday = True
        else:
            if a == b:
                today_is_birthday = True
        return today_is_birthday
    
    
def signin_user(request , user_obj) :
    """sign in user"""
    refresh = RefreshToken.for_user(user_obj)
    # check user birthday 
    today_is_birthday = check_user_birthday(user_obj)
    need_complete_profile = user_obj.need_complete       
    # user should change their password if they login successfully via this method. so:
    user_serialized = UserSerializer(
        user_obj,
        data ={"last_login": timezone.now()},
        partial=True,
        )
    if not user_serialized.is_valid():
        return validation_error(user_serialized)
    user_serialized.save()
    # successful login
    response_json = {
        "succeeded": True,
        "Authorization": 'Token '+str(refresh.access_token),
        "role": user_obj.role,
        "today_is_birthday": today_is_birthday,
    }
    # user log for LOGIN
    create_user_log(user_obj, request, kind=0)

    return Response(response_json, status=HTTP_200_OK)
    
    
def signup_user(request) :
    """signup user"""
    # check user birthday , role and mobile if there is one missing signup will be fail
    birthday = request.data.get("birthday")
    role = request.data.get("role")
    mobile = request.data.get("mobile")
    # if not birthday or role or mobile :
    #     return Response(
    #         data = {
    #             "succeeded" : False,
    #             "detail" : "birthday/role/mobile must be entered"  
    #         } ,
    #         status = HTTP_400_BAD_REQUEST
    #     )
    # user data
    # OPTIONAL data 
    password = make_password(request.data.get("password"))
    email = request.data.get("email")
    req = {
        "password": password,
        "birthday": birthday,
        "mobile": mobile,
        # NOTE becareful with this role if client pass ADMIN role the ADMIN user will be created
        "role": role,
        "email": email,
        "is_active": True, 
        "is_real": 1,
        "last_login": timezone.now()
    }
        
    user_serialized = UserSerializer(data=req)
    if not user_serialized.is_valid():
        return validation_error(user_serialized)
    # create user instance
    user_obj = user_serialized.save()  
    # create token
    token = RefreshToken.for_user(user_obj)
    # create log for LOGIN
    create_user_log(user_obj, request, kind=0)
        
    # TODO Security:  dont send Authorization TOKEN
    response_json = {
        "succeeded": True,
        "Authorization": f'Token {token.access_token}',
        "role": user_obj.role,
    }
        
    return Response(response_json, status=HTTP_200_OK)    

def check_otp(mobile , otp) :
    hashed_otp = cache.get(f"OTP:{mobile}")
    # otp has expired

    if not hashed_otp:
        return Response({
            "succeeded": False,
            'expired': True,
            'en_detail' : 'Get OTP code again.',
            'fa_detail' : 'مجدد درخواست کد دو عاملی داده شود', 
            'show': True  
            }, status=HTTP_400_BAD_REQUEST)

    # wrong otp
    if not check_password(otp , hashed_otp):
        return Response({
            "succeeded": False,
            'wrong_auth': True,
            'en_detail' : 'Get OTP code again.',
            'fa_detail' : 'مجدد درخواست کد دو عاملی داده شود', 
            'show': True 
            }, status=HTTP_400_BAD_REQUEST)
    return True
# # cache expire time
# EXPIRE_TIME = 60

# # create token for the user
# def create_tokens(contact , contact_type) :
#     if contact_type == "phone" :
#         user = User.objects.get(phone=contact)
#     elif contact_type == "email" :
#         user = User.objects.get(email=contact)
#     else:
#         raise ValueError("Invalid contact type")
#     access_token = str(AccessToken.for_user(user))
#     refresh_token = str(RefreshToken.for_user(user))
#     data = {'access' : access_token, 'refresh' : refresh_token}
#     return data

# # create otp for the user
# # user means that it is email or phone base on user prefence 
# # def create_otp(contact , contact_type) :
# #     # send the otp to the user
# #     if can_request_otp(contact) :
# #         otp = random.randint(100000,999999)
# #         otp_cache_key = f"otp:{contact}"
# #         cache.set(otp_cache_key, otp , timeout=EXPIRE_TIME)
# #         otp_time = datetime.now().replace(microsecond=0)
# #         time_cache_key = f"otp_last_request:{contact}"
# #         cache.set(time_cache_key , otp_time , timeout=EXPIRE_TIME)
# #         if contact_type == "email" :
# #             # create message log and send email
# #             message = Message.objects.create(email=contact , kind="email" ,type="otp")
# #             email = tasks.send_otp_email.apply_async(args=[contact , otp , message.pk])
    
# #         elif contact_type == "phone" : 
# #             # create message log and send sms
# #             message = Message.objects.create(phone=contact , kind="sms" ,type="otp")
# #             sms = tasks.send_otp_sms.apply_async(args=[contact , otp , message.pk])
# #         return otp
# #     return False

# # verify the otp
# # def verify_otp(contact , otp) :
# #     cache_key = f"otp:{contact}"
# #     stored_otp = cache.get(cache_key)
# #     last_time = cache.get(f"otp_last_request:{contact}")

# #     if last_time is None :
# #         return "expired"
# #     if str(stored_otp) == str(otp) :
# #         cache.delete(cache_key)
# #         cache.delete(f"otp_last_request:{contact}")
# #         return True
# #     else :
# #         return "invalid"

# # check that user can request otp or not
# # def can_request_otp(contact) :
# #         last_time = cache.get(f"otp_last_request:{contact}")
# #         print(last_time)
# #         time_now = datetime.now()
# #         if not last_time :
# #             return True
# #         expire_time = last_time + timedelta(seconds=EXPIRE_TIME)
# #         if time_now > expire_time :
# #             return True
# #         return False

# # check that user exist or not
# # def user_have_account(contact) :
# #     if '@' in contact :
# #         user = User.objects.filter(email=contact).exists()
# #     else :
# #         user = User.objects.filter(phone=contact).exists()
# #     if user :
# #         return True
# #     return False