from django.shortcuts import render
# third party imports
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
# local imports
from .serializers import PaymentSerializer
from employer.models import Employer
from employer.utils import employer_exists
# Create your views here.

class CreatePayment(APIView) :
    @swagger_auto_schema(
        operation_summary="create payment",
        operation_description="create payment",
        request_body=PaymentSerializer,
        responses={
            200 : "payment created successfully",
            400 : "invalid parameters",
            404 : "job seeker was not found"
        }
    )
    def post(self , request) :
        user = request.user
        employer = employer_exists(user)
        if not employer : 
            return Response(data={"detail" : "employer does not exists"} , status=status.HTTP_400_BAD_REQUEST)
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid() : 
            data = serializer.validated_data
            data['employer'] = employer
            serializer.save()
            return Response(data={"success" : True} , status=status.HTTP_200_OK)
        return Response(data={"detail" : serializer.errors} , status=status.HTTP_400_BAD_REQUEST)


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