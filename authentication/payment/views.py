from django.shortcuts import render
# third party imports
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema

from .models import Payment
# local imports
from .serializers import PaymentSerializer
from employer.models import Employer
from employer.utils import employer_exists
from . import utils
from .utils import verify_payment
from . import tasks

# Create your views here.

# class CreatePayment(APIView) :
#     @swagger_auto_schema(
#         operation_summary="create payment",
#         operation_description="create payment",
#         request_body=PaymentSerializer,
#         responses={
#             200 : "payment created successfully",
#             400 : "invalid parameters",
#             404 : "job seeker was not found"
#         }
#     )
    # def post(self , request) :
    #     user = request.user
    #     employer = employer_exists(user)
    #     if not employer :
    #         return Response(data={"detail" : "employer does not exists"} , status=status.HTTP_400_BAD_REQUEST)
    #     serializer = PaymentSerializer(data=request.data)
    #     if serializer.is_valid() :
    #         data = serializer.validated_data
    #         data['employer'] = employer
    #         serializer.save()
    #         return Response(data={"success" : True} , status=status.HTTP_200_OK)
    #     return Response(data={"detail" : serializer.errors} , status=status.HTTP_400_BAD_REQUEST)


class PaymentProcess(APIView) :
    def get(self , request) :
        user = request.user
        employer = employer_exists(user)
        if not employer:
            return Response(data={"detail": "employer does not exists"}, status=status.HTTP_400_BAD_REQUEST)
        # check if there is pending payment do not allow user to create payment again
        acitve_payment = Payment.objects.filter(employer=employer , status="pending")
        if acitve_payment.exists() :
            return Response(data={"success" : False , "error" : "there is active payment for you" , "fa_error" : "پرداختی فعالی برای شما وجود دارد"} , status=status.HTTP_400_BAD_REQUEST)
        # save the payment
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid() :
            data = serializer.validated_data
            amount = data['amount']
            # create the authority
            authority = utils.get_authority(amount)
            if authority is None:
                return Response(data={"error" : "process failed" , "fa_error" : "مشکلی در پرداخت به وجود آمده"} , status=status.HTTP_400_BAD_REQUEST)
            # create the payment url
            url = utils.payment_link(authority)
            payment = serializer.save(employer=employer , authority=authority)
            # cancel the payment if after 15 mintues payment was not successful
            # tasks.fail_payment_if_unpaid(payment.pk)
            # tasks.simple_task.apply_async(args=[payment.pk], countdown=1 * 15)
            # tasks.fail_payment_if_unpaid.apply_async(args=[payment.pk], countdown=1 * 15)
            return Response(data={"success": True , "payment_url" : url}, status=status.HTTP_200_OK)
        return Response(data={"success" : False , "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def post(self , request):
        user = request.user
        employer = employer_exists(user)
        if not employer:
            return Response(data={"detail": "employer does not exists"}, status=status.HTTP_400_BAD_REQUEST)
        # get the current pending payment
        try :
            user_pending_payment = Payment.objects.get(employer=employer , status="pending")
        except Payment.DoesNotExist:
            return Response(data={"success": False , "error" : "payment does not exists" , "fa_error" : "پرداختی با این مشخصات وجود ندارد" } , status=status.HTTP_404_NOT_FOUND)

        authority = user_pending_payment.authority
        amount = user_pending_payment.amount
        # if the purchase was failed
        if not verify_payment(authority, amount):
            user_pending_payment.status = "failed"
            user_pending_payment.save()
            return Response(data={"error" : "payment failed" , "fa_error" : "پرداخت ناموفق "}, status=status.HTTP_400_BAD_REQUEST)
            # if it was successful
        user_pending_payment.first().status = "completed"
        user_pending_payment.first().save()
        return Response(data={"success" : True , "fa_data" : "پرداخت موفق"})


# class Purchase(APIView) :
#     def post(self , request):


# import requests
# import json
#
# # ? sandbox merchant
# sandbox = "www"
#
# ZP_API_REQUEST = f"https://{sandbox}.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
# ZP_API_VERIFY = f"https://{sandbox}.zarinpal.com/pg/rest/WebGate/PaymentVerification.json"
# ZP_API_STARTPAY = f"https://{sandbox}.zarinpal.com/pg/StartPay/"
#
# amount = 1000  # Rial / Required
# description = "توضیحات مربوط به تراکنش را در این قسمت وارد کنید"  # Required
# phone = 'YOUR_PHONE_NUMBER'  # Optional
# # Important: need to edit for realy server.
# CallbackURL = 'http://127.0.0.1:8080/verify/'
# MERCHANT = "e6713db5-d035-422c-986c-b6d3d1c868ff"
#
# def send_request(request):
#     data = {
#         "MerchantID": MERCHANT,
#         "Amount": amount,
#         "Description": description,
#         "Phone": phone,
#         "CallbackURL": CallbackURL,
#     }
#     data = json.dumps(data)
#     # set content length by data
#     headers = {'content-type': 'application/json', 'content-length': str(len(data))}
#     try:
#         response = requests.post(ZP_API_REQUEST, data=data, headers=headers, timeout=10)
#         print(response)
#
#         if response.status_code == 200:
#             response = response.json()
#             if response['Status'] == 100:
#                 return {'status': True, 'url': ZP_API_STARTPAY + str(response['Authority']),
#                         'authority': response['Authority']}
#             else:
#                 return {'status': False, 'code': str(response['Status'])}
#         return response
#
#     except requests.exceptions.Timeout:
#         return {'status': False, 'code': 'timeout'}
#     except requests.exceptions.ConnectionError:
#         return {'status': False, 'code': 'connection error'}
#
#
# def verify(authority):
#     data = {
#         "MerchantID": MERCHANT,
#         "Amount": amount,
#         "Authority": authority,
#     }
#     data = json.dumps(data)
#     # set content length by data
#     headers = {'content-type': 'application/json', 'content-length': str(len(data))}
#     response = requests.post(ZP_API_VERIFY, data=data, headers=headers)
#
#     if response.status_code == 200:
#         response = response.json()
#         if response['Status'] == 100:
#             return {'status': True, 'RefID': response['RefID']}
#         else:
#             return {'status': False, 'code': str(response['Status'])}
#     return response

