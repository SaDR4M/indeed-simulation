from celery import shared_task
import urllib
import os
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
        # log_message.status = "sent"
        # verify the status 30 second later
        check_sms_status.apply_async(args=[message_id , log_message.pk] , countdown=30)
    elif data['return']['status'] in [403 , 418] :
        log_message.status = "failed"
        return "error with api/account"
    else :
        log_message.status = "failed"
    log_message.save()
        
    # update the message status
    # if data['return']['status'] == 200 :
    #     return data
    # return data

@shared_task
def send_otp_sms(phone , otp ,  log_pk) :
    message = f"{otp} : کد اعتبار سنجی شما"
    sms = send_sms.apply_async(args=[phone , message , log_pk])
    # result = sms.get()
    # if not result :
    #     return False
    # return result

@shared_task
def send_login_sms(phone , log_pk) : 
    message = f"شم با موفقیت وارد شدید"
    sms = send_sms.apply_async(args=[phone , message , log_pk])
    # result = sms.get()
    # if not result :
    #     return False
    # return result

@shared_task
def send_order_sms(phone , order_id , log_pk) : 
    message = f"سفارش شما با شماره سفارش {order_id} ثبت شد"
    sms = send_sms.apply_async(args=[phone , message , log_pk])
    # result = sms.get()
    # if not result :
    #     return False
    # return result
# response = requests.get(url=f"https://api.kavenegar.com/v1/{API_KEY}/sms/status.json?messageid=1552292381")
# print(response.json())

@shared_task(bind=True , default_retry_delay=60 , max_retries=5)
def check_sms_status(self , message_id , log_pk , retry_count=0) :
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
    
    print(data)
    # message status
    if data['return']['status'] == 200 :
            status = data['entries'][0]['status']
            if status in [1 , 2]:
                log_message.status = "pending"
                if retry_count < 5 :
                    self.apply_async(args=[message_id , log_message.pk , retry_count + 1] , countdown=30)
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
        
    elif data['return']['status'] in [403, 418]:  # API error
        return "Error with API/account. No further retries."
    else:
        # Retry for unexpected errors
        if retry_count < 5 :
            self.retry(args=[message_id, log_pk,retry_count + 1], countdown=30)
        return "Error while sending message"