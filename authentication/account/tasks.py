import os
import urllib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
# local imports

# third party imports
from celery import shared_task
import requests
import dotenv
from .models import Message
dotenv.load_dotenv(dotenv_path="../.env")

# API_KEY = os.getenv('SMS_API_KEY')

@shared_task
def send_sms(phone , message , log_pk) :
    API_KEY = os.getenv('SMS_API_KEY')
    url = f"https://api.kavenegar.com/v1/{API_KEY}/sms/send.json"

    # get the message
    try :
        log_message = Message.objects.get(pk=log_pk)
    except Message.DoesNotExist :
        return "message does not exists"
    except Exception as e:
        return f"error while getting the log , error : {e}"

    data = {
        "receptor" : phone,
        "message" : message,
    }
    # send the message
    try :
        response = requests.post(url , data=data)
    except :
        #log_message.status = "failed"
        #log_message.save()
        return f"error occured while sending sms , error : {e}"
    data = response.json()
    status = data['return']['status']
    print(data)
    if status == 200 :
        message_id = data['entries'][0]['messageid']
        log_message.message_id = message_id
        # verify the status 60 second later
        check_sms_status.apply_async(args=[message_id , log_message.pk] , countdown=60)
    elif data['return']['status'] in [403 , 418] :
        log_message.status = "failed"
        return "error with api/account"
    else :
        log_message.status = "failed"
    log_message.save()
        

@shared_task
def send_otp_sms(phone , otp ,  log_pk) :
    message = f"{otp} : کد اعتبار سنجی شما"
    try :
        sms = send_sms.apply_async(args=[phone , message , log_pk])
    except Exception as e:
        print(f"Error whils sending otp sms : {e}")

@shared_task
def send_login_sms(phone , log_pk) : 
    message = f"شم با موفقیت وارد شدید"
    try :
        sms = send_sms.apply_async(args=[phone , message , log_pk])
    except Exception as e:
        print(f"Error whils sending otp sms : {e}")

@shared_task
def send_order_sms(phone , order_id , log_pk) : 
    message = f"سفارش شما با شماره سفارش {order_id} ثبت شد"
    try :
        sms = send_sms.apply_async(args=[phone , message , log_pk])
    except Exception as e:
        print(f"Error whils sending otp sms : {e}")


@shared_task(bind=True , default_retry_delay=60 , max_retries=5)
def check_sms_status(self , message_id , log_pk , retry_count=0) :
    # kave negar
    API_KEY = os.getenv('SMS_API_KEY')
    response = requests.get(url=f"https://api.kavenegar.com/v1/{API_KEY}/sms/status.json?messageid={message_id}")
    data = response.json()
    
    # log message
    try :
        log_message = Message.objects.get(pk=log_pk)
    except Message.DoesNotExist :
        return "message does not exists"
    except Exception as e:
        return f"error while getting the log error : {e}"
    
    # message status
    if data['return']['status'] == 200 :
            status = data['entries'][0]['status']
            if status in [1 , 2]:
                log_message.status = "pending"
                if retry_count < 5 :
                    self.apply_async(args=[message_id , log_message.pk , retry_count + 1] , countdown=15)
            elif status in [4 , 5] :
                log_message.status = "sent"
            elif status == 6 :
                log_message.status = "failed"
            elif status == 10 :
                log_message.status = "delivered"
            elif status == 11 :
                log_message.status = "undelivered"
            elif status == 14 :
                return "message is blocked by user"
            else :
                log_message.status = "failed"
            log_message.save()     
            return f"status saved , message status {log_message.status}"
        
     # عدم موجودی حساب یا مشکل از حساب
    elif data['return']['status'] in [403, 418]: 
        return "Error with API/account. No further retries."
    else:
        # Retry for unexpected errors
        if retry_count < 5 :
            self.retry(args=[message_id, log_pk,retry_count + 1], countdown=15)
        return "Error while sending message"
    
# email

@shared_task(default_retry_delay=60 , max_retries=5)
def send_email(subject , content , recipient , log_id) :
    SENDER_EMAIL = "mjanloo83@gmail.com"
    APP_PASSWORD = "hrrm gqmd zbuo urho"
    
    # using html content for email
    message = MIMEMultipart("alternative")
    message["subject"] = subject
    message.attach(MIMEText(content, "html", "utf-8"))
    # getting message log
    try :
        log_message = Message.objects.get(pk=log_id)
    except Message.DoesNotExist() :
        return "message does not exists"   
     
    try :
        server = smtplib.SMTP("smtp.gmail.com" , 587)
        server.starttls()
        server.login(SENDER_EMAIL , APP_PASSWORD)
        server.sendmail("mjanloo83@gmail.com" , recipient , message.as_string() )
    
    except smtplib.SMTPRecipientsRefused:
        log_message.status = "failed"
        print("Error : recipient's email address was refused")
    except smtplib.SMTPSenderRefused:
        log_message.status = "failed"
        print("Error : sender email address was refused")
    except smtplib.SMTPDataError:
        log_message.status = "failed"
        print("Error : the smtp server refused the email content")
    except Exception as e :
        log_message.status = "failed"
        print(f"error : {e}")
    finally :
        log_message.status = "sent"
        server.quit()
    log_message.save()



@shared_task(default_retry_delay=60 , max_retries=5)
def send_order_email(recipient , order_id , log_id) : 
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
        send_email.apply_async(args=["سفارش" , content , recipient , log_id])
    except Exception as e :
        print(f"Error ocured {e}")
        
@shared_task(default_retry_delay=60 , max_retries=5)    
def send_otp_email(recipient , otp , log_id) : 
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
        send_email.apply_async(args= ["ورود به حساب" , content , recipient , log_id])
    except Exception as e :
        print(f"Error ocured {e}")