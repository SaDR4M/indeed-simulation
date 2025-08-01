import os
import random
import requests
import urllib
from django.conf import settings
from dotenv import load_dotenv
load_dotenv(dotenv_path='../.env')
# local imports
from payment.models import Payment
from order.models import CartItem

CALLBACK_URL = "http://127.0.0.1:8000/account/data"
DESCRIPTION = 'خرید محصول'
MERCHANT_ID = os.getenv('MERCHANT_ID')


def get_authority(amount) :
    print(
        "authority test"
    )
    try :
        url = 'https://payment.zarinpal.com/pg/v4/payment/request.json'
        response = requests.post(url , {
            "amount" : int(amount),
            "description" : DESCRIPTION,
            "merchant_id" : MERCHANT_ID,
            "callback_url" : CALLBACK_URL
        })
        data = response.json()['data']
    except Exception as e :
        return f"Error when getting the authority : {e}"
    if data :
        if data['code'] == 100:
            authority = data['authority']
            return authority
    print("success")
    return None

def payment_link(authority) :
        url = f"https://payment.zarinpal.com/pg/StartPay/{authority}"
        return url

def verify_payment(authority, amount):
    try :
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
    except Exception as e :
        return False


def create_random_number() :
    number = random.randint(300000 , 1000000)
    payment = Payment.objects.filter(payment_id=number)
    if payment.exists() :
        create_random_number()
    return number

def calc_order_amount(employer) : 
    total_price = 0
    cart_items = CartItem.objects.filter(cart__employer=employer , cart__active=True)
    if not cart_items.exists() :
        return None
    for item in cart_items :
        total_price += item.package.price
    # price of the urgent offers
    # if item.package.type == "offer" and item.package.priority == "urgent" :
    #     total_price = total_price * 1.6
    return total_price


API_KEY = os.getenv('SMS_API_KEY')
def send_sms(phone , message) :
    url = f"https://api.kavenegar.com/v1/{API_KEY}/sms/send.json"
    
    # encode_message = urllib.parse.quote("این یک پیام تست است")
    data = {
        "receptor" : phone,
        "message" : message,

    }
    response = requests.post(url , data=data)

