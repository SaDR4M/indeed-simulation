import os
import random
import requests
import urllib
from django.conf import settings
from dotenv import load_dotenv
load_dotenv(dotenv_path='../.env')
# local imports
from .models import Payment
from employer.models import EmployerCartItem

CALLBACK_URL = "http://127.0.0.1:8000/account/data"
DESCRIPTION = 'خرید محصول'
MERCHANT_ID = os.getenv('MERCHANT_ID')


def get_authority(amount) :
    url = 'https://payment.zarinpal.com/pg/v4/payment/request.json'
    response = requests.post(url , {
        "amount" : int(amount),
        "description" : DESCRIPTION,
        "merchant_id" : MERCHANT_ID,
        "callback_url" : CALLBACK_URL
    })
    data = response.json()['data']
    if data :
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
    data = response.json()['data']
    if data :
        if data['code'] == 100 or data['code'] == 101:
            return data
    return False


def create_random_number() :
    number = random.randint(300000 , 1000000)
    payment = Payment.objects.filter(payment_id=number)
    if payment.exists() :
        create_random_number()
    return number

def calc_order_amount(employer) : 
    total_price = 0
    cart_items = EmployerCartItem.objects.filter(cart__employer=employer)
    if not cart_items.exists() :
        return None
    for item in cart_items :
        total_price += item.package.price
    return total_price


API_KEY = os.getenv('SMS_API_KEY')
def send_sms(phone , message) :
    url = f"https://api.kavenegar.com/v1/{API_KEY}/sms/send.json"
    
    # encode_message = urllib.parse.quote("این یک پیام تست است")
    data = {
        "receptor" : phone,
        # 'sneder' : "2000500666",
        "message" : message,

    }
    response = requests.post(url , data=data)
    print(response.json())
# send_sms(09036700953 , "سلام")
response = requests.get(url=f"https://api.kavenegar.com/v1/{API_KEY}/sms/status.json?messageid=1557328738")
print(response.json())