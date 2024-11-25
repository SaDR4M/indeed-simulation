# Standard Library Imports
import random
from datetime import datetime, timedelta

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'authentication.settings')



# Third-Party Imports
from django.core.cache import cache
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
import requests
# Local App Imports
from .models import User


# cache expire time
EXPIRE_TIME = 25

# create token for the user
def create_tokens(phone) :
    user = User.objects.get(phone=phone)
    access_token = str(AccessToken.for_user(user))
    refresh_token = str(RefreshToken.for_user(user))
    data = {'access' : access_token, 'refresh' : refresh_token}
    return data

# create otp for the user
def create_otp(user_phone) :
    otp = random.randint(100000,999999)
    otp_cache_key = f"otp:{user_phone}"
    cache.set(otp_cache_key, otp , timeout=EXPIRE_TIME)
    otp_time = datetime.now().replace(microsecond=0)
    time_cache_key = f"otp_last_request:{user_phone}"
    cache.set(time_cache_key , otp_time , timeout=EXPIRE_TIME)
    return otp

# verify the otp
def verify_otp(user_phone , otp) :
    cache_key = f"otp:{user_phone}"
    stored_otp = cache.get(cache_key)
    last_time = cache.get(f"otp_last_request:{user_phone}")

    if last_time is None :
        return "expired"
    if str(stored_otp) == str(otp) :
        cache.delete(cache_key)
        cache.delete(f"otp_last_request:{user_phone}")
        return True
    else :
        return "invalid"

# check that user can request otp or not
def can_request_otp(user_phone ) :
        last_time = cache.get(f"otp_last_request:{user_phone}")
        time_now = datetime.now()
        if not last_time :
            return True
        expire_time = last_time + timedelta(seconds=EXPIRE_TIME)
        if time_now > expire_time :
            return True
        return False

# check that user exist or not
def user_have_account(phone) :
    user = User.objects.filter(phone=phone).exists()
    if user :
        return True
    return False

