


# built in imports
from datetime import datetime
# django & rest imports
from django.utils.timezone import make_aware
# third party imports
from celery import shared_task
from icecream import ic
from decouple import config
# local imports
from core.kavenegar import *

'58546C51517035384E664B44345970343258654E2F5132383555714C69437876616358682B6B444E777A673D'

@shared_task
def send_otp(receptor, token,token2, type, sender="100045312", user=None):
    # only call to iranian users
    if not receptor.startswith(('98', '+98', '0098')):
        return None
    try:

        api_key = config("KAVENEGAR_API_KEY")
        api = KavenegarAPI(
            api_key , timeout=20
        )
        params = {
            'receptor': str(receptor),
            'template': '45312-login-otp',
            'token': str(token),
            'token2': str(token),
            'type': 'sms',# sms vs call
        }   
        response = api.verify_lookup(params)
        print(response)
    except HTTPException as e: 
        print(e)

@shared_task
def send_sms(receptor, message,  smsCategoryCode, sender="100045312", user=None): 
    
    # only call to iranian users
    if not receptor.startswith(('98', '+98', '0098')):
        return None
    try:
        api_key = config("KAVENEGAR_API_KEY")
        api = KavenegarAPI(
            api_key , timeout=20
        )
        params = {
            "receptor": str(receptor),
            "message": message,
            "sender": str(sender),
        }

        response = api.sms_send(params)
        status = response["return"]["status"]

        if int(status) == 200:
            req = {
                "params_receptor": str(receptor),
                "params_message": str(message),
                "params_sender": str(sender),
                "validation": False,
                "status": response["return"]["status"],
                "message": response["return"]["message"],
                "messageid": response["entries"][0]["messageid"],
                "message": response["entries"][0]["message"],
                "status": response["entries"][0]["status"],
                "statustext": response["entries"][0]["statustext"],
                "sender": response["entries"][0]["sender"],
                "receptor": response["entries"][0]["receptor"],
                "date": make_aware(
                    datetime.fromtimestamp(
                        float(response["entries"][0]["date"]))
                ),
                "smsCat": smsCategoryCode,
                "cost": response["entries"][0]["cost"],
                "send_by": user,
                "is_sending": True,
            }

        else:
            req = {
                "status": response["return"]["status"],
                "message": response["return"]["message"],
            }
        # sms_logs_serialized = SMSLogSerializer(data=req)
        # sms_logs_serialized.is_valid(raise_exception=True)
        # sms_logs_serialized.save()

        # #developing issues
        # 400
        # 412
        # 413

        # #kavenegar account issues
        # 401
        # 403
        # 418
        # 505

        # #unsuccess
        # 402

        # #try again
        # 409

        # #invalid receptor
        # 411

        # # others
        # 414
        # 417
        # 419
        # 502
        # 503
        # 504
        # 506
        # 507
        # 601
        # 602
        # 603

    except HTTPException as e:
        print(str(e))
    # except APIException as e: 
    #     print(str(e))