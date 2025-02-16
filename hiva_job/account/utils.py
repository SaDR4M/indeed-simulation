# Standard Library Imports
import random
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# import os 
# import sys
# sys.path.insert(0, "e:\\project\\hiva_job")
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# print(sys.path) 
# import django
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hiva_job.settings")
# django.setup()
# Third-Party Imports
from django.core.cache import cache
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
import requests
# Local App Imports
from account.models import User , Message
from account import tasks


# cache expire time
EXPIRE_TIME = 60

# create token for the user
def create_tokens(contact , contact_type) :
    if contact_type == "phone" :
        user = User.objects.get(phone=contact)
    elif contact_type == "email" :
        user = User.objects.get(email=contact)
    else:
        raise ValueError("Invalid contact type")
    access_token = str(AccessToken.for_user(user))
    refresh_token = str(RefreshToken.for_user(user))
    data = {'access' : access_token, 'refresh' : refresh_token}
    return data

# create otp for the user
# user means that it is email or phone base on user prefence 
def create_otp(contact , contact_type) :
    # send the otp to the user
    if can_request_otp(contact) :
        otp = random.randint(100000,999999)
        otp_cache_key = f"otp:{contact}"
        cache.set(otp_cache_key, otp , timeout=EXPIRE_TIME)
        otp_time = datetime.now().replace(microsecond=0)
        time_cache_key = f"otp_last_request:{contact}"
        cache.set(time_cache_key , otp_time , timeout=EXPIRE_TIME)
        if contact_type == "email" :
            # create message log and send email
            message = Message.objects.create(email=contact , kind="email" ,type="otp")
            email = tasks.send_otp_email.apply_async(args=[contact , otp , message.pk])
    
        elif contact_type == "phone" : 
            # create message log and send sms
            message = Message.objects.create(phone=contact , kind="sms" ,type="otp")
            sms = tasks.send_otp_sms.apply_async(args=[contact , otp , message.pk])
        return otp
    return False

# verify the otp
def verify_otp(contact , otp) :
    cache_key = f"otp:{contact}"
    stored_otp = cache.get(cache_key)
    last_time = cache.get(f"otp_last_request:{contact}")

    if last_time is None :
        return "expired"
    if str(stored_otp) == str(otp) :
        cache.delete(cache_key)
        cache.delete(f"otp_last_request:{contact}")
        return True
    else :
        return "invalid"

# check that user can request otp or not
def can_request_otp(contact) :
        last_time = cache.get(f"otp_last_request:{contact}")
        print(last_time)
        time_now = datetime.now()
        if not last_time :
            return True
        expire_time = last_time + timedelta(seconds=EXPIRE_TIME)
        if time_now > expire_time :
            return True
        return False

# check that user exist or not
def user_have_account(contact) :
    if '@' in contact :
        user = User.objects.filter(email=contact).exists()
    else :
        user = User.objects.filter(phone=contact).exists()
    if user :
        return True
    return False

        
