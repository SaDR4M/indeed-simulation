import requests
from django.conf import settings

CALLBACK_URL = "http://127.0.0.1:8000/account/data"
DESCRIPTION = 'خرید محصول'
MERCHANT_ID = 'e6713db5-d035-422c-986c-b6d3d1c868ff'

def get_authority(amount) :
    url = 'https://payment.zarinpal.com/pg/v4/payment/request.json'
    response = requests.post(url , {
        "amount" : int(amount),
        "description" : DESCRIPTION,
        "merchant_id" : MERCHANT_ID,
        "callback_url" : CALLBACK_URL
    })
    data = response.json()['data']
    if data['code'] == 100:
        authority = data['authority']
        return authority
    return None

def payment_link(authority) :
        url = f"https://payment.zarinpal.com/pg/StartPay/{authority}"
        return url

def verify_payment(authority, amount):
    url = 'https://payment.zarinpal.com/pg/v4/payment/verify.json'
    response = requests.post(url , {
        "authority" : authority,
        "amount" : int(amount),
        'merchant_id' : MERCHANT_ID,
    })
    data = response.json()
    # print(response.json())
    if data['data'] :
        if data['data']['code'] == 100 or data['data']['code'] == 101:
            return data
    return False

authority = get_authority(10000)
link = payment_link(authority)
verify_payment(authority, 10000)
print(authority , link)
print(verify_payment(authority, 10000))
