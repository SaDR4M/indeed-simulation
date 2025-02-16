# built in
from datetime import datetime
# django & rest imports
from django.utils.timezone import make_aware
# third party
from decouple import config
from celery import shared_task
# local imports
from core.kavenegar import *


@shared_task
def make_call(receptor, message, maxDuration =  100 , caller="09124462808", user=None ): 
    # only call to iranian users
    if not receptor.startswith(('98', '+98', '0098')):
        return None
    try:
        api_key = config("KAVENEGAR_API_KEY")
        api = KavenegarAPI(
            api_key
        )
        params = {
            "receptor": str(receptor),
            "type" : 'call',
            "token" : str(message),
            "template" :'aspOperatorVerifyCall'
        }

        response = api.verify_lookup(params)
        status = response["return"]["status"]
        if int(status) == 200:

            req = {
                "params_receptor": str(receptor),
                "params_caller": str(caller),
                "validation": False,
                "status": response["return"]["status"],
                "status": response["entries"][0]["status"],
                "statustext": response["entries"][0]["statustext"],
                "receptor": response["entries"][0]["receptor"],
                "date": make_aware(
                    datetime.fromtimestamp(
                        float(response["entries"][0]["date"]))
                ),
                "maxDuration": 100,
                "template":"aspOperatorVerifyCall",
                "type" : "call",
                "cost": response["entries"][0]["cost"],
                "send_by": user,
                "is_sending": True,
            }

        else:
            req = {
                "status": response["return"]["status"],
                "message": response["return"]["message"],
            }

        # developing issues
        # 400
        # 412
        # 413

        # kavenegar account issues
        # 401
        # 403
        # 418
        # 505

        # unsuccess
        # 402

        # try again
        # 409

        # invalid receptor
        # 411

        # others
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

