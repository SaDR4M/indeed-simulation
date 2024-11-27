# Standard Library Imports
import random
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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

def send_email(subject , content , recipient="mjanloo83@gmail.com") :
    SENDER_EMAIL = "mjanloo83@gmail.com"
    APP_PASSWORD = "hrrm gqmd zbuo urho"
    
    # using html content for email
    message = MIMEMultipart("alternative")
    message["subject"] = subject
    message.attach(MIMEText(content, "html", "utf-8"))
    
    try :
        server = smtplib.SMTP("smtp.gmail.com" , 587)
        server.starttls()
        server.login(SENDER_EMAIL , APP_PASSWORD)
        server.sendmail("mjanloo83@gmail.com" , recipient , message.as_string() )
    
    except smtplib.SMTPRecipientsRefused:
        print("Error: The recipient's email address was refused by the server.")
    except smtplib.SMTPSenderRefused:
        print("Error: The sender's email address was refused by the server.")
    except smtplib.SMTPDataError:
        print("Error: The SMTP server refused the email content.")
    except Exception as e :
        print(f"error : {e}")
    finally :
        server.quit()




def send_order_email(recipient , order_id) : 
    content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; direction: rtl; text-align: right;">
        <div style="max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
            <h2 style="color: #2196F3; text-align: center;">تأیید سفارش</h2>
            <p>کاربر عزیز،</p>
            <p>از سفارش شما متشکریم! شماره سفارش شما به شرح زیر است:</p>
            <div style="text-align: center; margin: 20px 0;">
                <span style="font-size: 24px; font-weight: bold; color: #333;">{order_id}</span>
            </div>
            <p>ما در حال آماده‌سازی سفارش شما برای ارسال هستیم. به زودی ایمیل دیگری دریافت خواهید کرد که اطلاعات ارسال کالا را شامل می‌شود.</p>
            <p style="margin-top: 30px;">در صورتی که سوالی دارید، با ما تماس بگیرید.</p>
            <p>با تشکر از خرید شما!<br>تیم شرکت شما</p>
        </div>
    </body>
    </html>
    """
    try :
        send_email("سفارش" , content , recipient)
    except Exception as e :
        print(f"Error ocured {e}")
        

def send_otp_email(recipient , otp) : 
    content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; direction: rtl; text-align: right;">
        <div style="max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
            <h2 style="color: #4CAF50; text-align: center;">کد تایید شما</h2>
            <p>کاربر گرامی،</p>
            <p>برای تکمیل فرآیند تأیید هویت خود از کد زیر استفاده کنید:</p>
            <div style="text-align: center; margin: 20px 0;">
                <span style="font-size: 24px; font-weight: bold; color: #333;">{otp}</span>
            </div>
            <p>اگر این کد را درخواست نکرده‌اید، لطفاً این ایمیل را نادیده بگیرید.</p>
            <p style="margin-top: 30px;">با تشکر،<br>تیم شرکت شما</p>
        </div>
    </body>
    </html>
    """
    try :
        send_email("ورود به حساب" , content , recipient)
    except Exception as e :
        print(f"Error ocured {e}")
        
send_otp_email("mjanloo83@gmail.com" , "12345" )