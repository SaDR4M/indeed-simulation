# built-in
import re
from user_agents import parse
import uuid
# django & rest imports
from django.core.cache import cache
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.validators import ValidationError
from django.utils import timezone
from django.contrib.auth.hashers import check_password
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.status import HTTP_200_OK , HTTP_400_BAD_REQUEST
from django.core.cache import cache
from django.utils.timezone import datetime
# third party
from icecream import ic
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



def create_token(user:object) :
    """create token for the user"""
    token = RefreshToken.for_user(user)
    # login the user
    data = {
            "Authorization" : f"Token {token.access_token}"
    }
    return data
    
    
    
def create_otp(mobile) :
    # create otp code
    otp = str(uuid.uuid4().int)[:5]
    key = f'OTP:{mobile}'
        
    if cache.get(key):  # pass the sms code sending if we already have send an sms to user
        return Response(
            data = {
            "succeeded": False,
            "remain_time": cache.ttl(key),
            }, 
            status=HTTP_200_OK
        )
    return otp

def check_user_birthday(user) :
        today = datetime.today().date()
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
    

def check_user_existence(mobile , role) :
    try :
        user = User.objects.get(mobile=mobile , role=role)
    except User.DoesNotExist:
        return Response(
            data = {
                "en_detail" : "Invalid mobile or password" ,
                "fa_detail" : "شماره یا رمز وارد شده اشتباه است"
                } ,
            status = HTTP_400_BAD_REQUEST)
    return user



    
    
    
    
    
    
def signin_user(request , user_obj) :
    """sign in user with OTP"""
    refresh = RefreshToken.for_user(user_obj)
    # check user birthday 
    today_is_birthday = check_user_birthday(user_obj)
    # need_complete_profile = user_obj.need_complete       
    # user should change their password if they login successfully via this method. so:
    user_serialized = UserSerializer(
        user_obj,
        data ={"last_login": timezone.now()},
        partial=True,
        )
    if not user_serialized.is_valid():
        return validation_error(user_serialized)
    user = user_serialized.save()
    # successful login
    # create token for user
    token = create_token(user)
    token.update({
        "succeeded": True,
        "today_is_birthday": today_is_birthday,
    })
    # user log for LOGIN
    create_user_log(user_obj, request, kind=0)

    return Response(token, status=HTTP_200_OK)
    
    
def signup_user(request:object) :
    """signup user"""
    # TODO add regex for password
    # check user birthday , role and mobile if there is one missing signup will be fail
    birthday = request.data.get("birthday")
    role = request.data.get("role")
    mobile = request.data.get("mobile")
    password = request.data.get("password")
    # validate inputs
    if not birthday or not role or not mobile or not password :
        return Response(
            data = {
                "succeeded" : False,
                "detail" : "birthday/role/mobile/password must be entered"  
            } ,
            status = HTTP_400_BAD_REQUEST
        )
    # ADMIN role
    if role == 10 :
        return Response(status=403)
    # if user is employer it's not real person => this might change
    if role == 1 :
        is_real = 0
    # if user is job seeker it's real person
    else :
        is_real = 1
    # check user exists or not
    # if the user is Repsonse it means user does not exists so we can create the user 
    user = check_user_existence(mobile , role)
    if not isinstance(user , Response) :
        return Response(
                data={
                    "en_detail" : "user exists" ,
                    "fa_detail" : " کاربری با این مشخصات وجود دارد"
                } , 
                status=HTTP_400_BAD_REQUEST
            )
    # validate user password
    validated_pass = validate_user_password(password)
    # if something went wrong for the password validation
    if isinstance(validated_pass , Response) :
        return validated_pass
    # user data
    # NOTE becareful with role if client pass ADMIN role the ADMIN user will be created
    hashed_password = make_password(password)
    req = {
        "password": hashed_password,
        "birthday": birthday,
        "mobile": mobile,
        "role": role,
        "is_active": True, 
        "is_real": is_real,
        "last_login": timezone.now()
    }   
    user_serialized = UserSerializer(data=req)
    if not user_serialized.is_valid():
        return validation_error(user_serialized)
    # create user instance 
    user_obj = user_serialized.save()  
    # create log for LOGIN
    create_user_log(user_obj, request, kind=0)
    # create token
    token = create_token(user_obj)
    # user birthday
    today_is_birthday = check_user_birthday(user_obj)
    # TODO Security:  dont send Authorization TOKEN
    token.update({
        "succeeded": True,
        "today_is_birthday" : today_is_birthday
    })
        
    return Response(token, status=HTTP_200_OK)    

def check_otp(mobile:str , otp:str) :
    hashed_otp = cache.get(f"OTP:{mobile}")
    
    # otp has expired
    if not hashed_otp:
        return Response({
            "succeeded": False,
            'expired': True,
            'en_detail' : 'Get OTP code again.',
            'fa_detail' : 'مجدد درخواست کد دو عاملی داده شود', 
            'show': True ,
            'time' : 3000,
            }, status=HTTP_400_BAD_REQUEST)

    # wrong otp
    if not check_password(otp , hashed_otp):
        return Response({
            "succeeded": False,
            'show': True,
            'wrong_auth': True,
            'en_detail' : 'OTP is wrong',
            'fa_detail' : 'کد وارد شده صحیح نمی باشد', 
            'time' : 3000,
            }, status=HTTP_400_BAD_REQUEST)
    return True

def signin_user_wp(mobile:str , role:str , password:str , request:object) :
    """signin user with password and the mobile number"""
    # if there is no user with the mobile number
    user = check_user_existence(mobile , role)
    if isinstance(user , Response) :
        return user
    today_is_birthday = check_user_birthday(user)
    # create token if the user exist and password is set
    if user is not None and user.password is not None:
        if user.check_password(password):
            # create user log
            create_user_log(user , request , kind=0)
            token = create_token(user)
            token.update(
                {
                   "succeeded" : True,
                   "today_is_birthday" : today_is_birthday
                }
            )
            return Response(data=token , status=HTTP_200_OK)
        # if password is wrong
        return Response(
            data = {
                "en_detail" : "Invalid mobile or password" ,
                "fa_detail" : "شماره یا رمز وارد شده اشتباه است"
                } ,
            status = HTTP_400_BAD_REQUEST)
    # if user exists but password is not set
    if user is not None and user.password is None :
        return Response(
            data = {
                "en_detail" : "Password is not set for the account",
                "fa_detail" : "رمز عبور برای اکانت تعیین نشده است"
            } ,
            status=HTTP_400_BAD_REQUEST
        )


def validate_user_password(password:str) :
    """validate the password then update user password"""
    # validate new password => min len 8 , cannot be just numeric
    try :
        validate_password(password)
    except ValidationError as e:
        return Response(
            data = {
                "en_detail" : e.messages
            }
        )
    return True



def validate_user_mobile(mobile) :
    mobile_validate = re.search("^(0|0098|98|\+98)9(0[1-5]|[1 3]\d|2[0-2]|9[1 8 9])\d{7}$", str(mobile))
    if not mobile_validate:
        response_json = {
            'succeeded': False,
            'show': True,
            'en_detail': 'Mobile is not correct',
            'fa_detail': 'ساختار شماره تلفن همراه نادرست است',
            'time' : 3000,
        }
        return Response(response_json, status=HTTP_400_BAD_REQUEST)
    return True

def update_user_password(user:object , old_password:str , new_password:str , confirm_password:str ) :
    """update user password"""
    # for password change
    # the old password and user password are not same
    if not check_password(old_password , user.password) :
        return Response(
            data = {
                "succeeded" : False,
                "show" : True,
                "time" : 3000,
                "en_detail" : "Invalid password",
                "fa_detail" : "پسورد وارد شده نامعتبر است"
            },
            status=HTTP_400_BAD_REQUEST
        )
        
    if new_password and confirm_password :
        # check passwords match or not
        if new_password != confirm_password:
            return Response(
                data = {
                    "succeeded" : False,
                    "show" : True,
                    'time' : 3000,                   
                    "en_detail": "password must match",
                    "fa_detail" : "پسوردهای وارد شده مطابقت ندارند",
                },
                status = HTTP_400_BAD_REQUEST)
        # user cannot set the old password as new password
        if old_password == new_password :
            return Response(
                    data = {
                    "succeeded" : False,
                    "show" : True,
                    "time" : 3000,
                    "en_detail" : "current password cannot be set as new password",
                    "fa_detail" : "پسورد فعلی به عنوان پسورد جدید مورد قبول نمی باشد"
                }
            )

        validated_pass = validate_user_password(new_password)
        # if something went wrong for the password validation
        if isinstance(validated_pass , Response) :
            return validated_pass
        else :
            # update user password
            user.set_password(new_password)
            user.save()
            return Response(
                data = {
                    "succeeded" : True,
                    "show" : True,
                    'time' : 3000,
                    "en_detail" : "password changed successfully",
                    "fa_detail" : "پسورد با موفقیت تغییر کرد"
                },
                status=HTTP_200_OK
            )   
        
    return Response(
            data = {
                "en_detail" : "new password and confirm password must be entered",
                "fa_detail" : "پسورد جدید و تکرار آن باید وارد شوند"
            },
            status = HTTP_400_BAD_REQUEST
        )
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