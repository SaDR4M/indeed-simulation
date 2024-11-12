# Standard Library Imports


# Third-Party Imports
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


# Django Imports
from django.contrib.auth.password_validation import validate_password
from django.core.validators import ValidationError, validate_email


# Local App Imports
from .models import User
from .serializer import UpdateCredential
from .utils import (
    verify_otp,
    user_have_account,
    create_otp,
    create_tokens,
    can_request_otp,
    EXPIRE_TIME
)
from . import docs

# Create your views here.

# sign in the user with password
class SignIn(APIView):
        # permission_classes = [IsAdminUser]
        @swagger_auto_schema(
                operation_description=docs.sign_in_document['operation_description'],
                operation_summary=docs.sign_in_document['operation_summary'],
                request_body=docs.sign_in_document['request_body'],
                responses=docs.sign_in_document['responses'],
        )

        def post(self , request):

            phone = request.data.get("phone")
            password = request.data.get('password')
            # check if the user phone or password were entered or not
            if not phone and not password :
                return Response(data={"detail" : "phone number and password are missing"} , status=status.HTTP_400_BAD_REQUEST)
            if phone is None:
                return Response(data={"detail" : "phone number is missing"} , status=status.HTTP_400_BAD_REQUEST)
            if password is None:
               return Response(data={"detail" : "password is missing"} , status=status.HTTP_400_BAD_REQUEST)


            # check the user
            try :
                user = User.objects.get(phone=phone)
            except User.DoesNotExist:
                return Response(data={"detail" : "user not found"} , status=status.HTTP_404_NOT_FOUND)

            # create token if the user exist
            if user is not None and user.password is not None:
                if user.check_password(password):
                    tokens = create_tokens(phone)
                    return Response(data={"data" : "login successfully" , "tokens" : tokens} , status=status.HTTP_201_CREATED)
                return Response(data={"detail" : "invalid credentials"} , status=status.HTTP_400_BAD_REQUEST)

            # check if username exist or not
            if not User.objects.filter(phone=phone).exists():
                return Response(data={"detail" :"user does not exists"} , status=status.HTTP_404_NOT_FOUND)




# add/update credentials info
class UpdateCredential(APIView) :
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description = docs.update_credential_document['operation_description'],
        operation_summary = docs.update_credential_document['operation_summary'],
        request_body = docs.update_credential_document['request_body'],
        responses = docs.update_credential_document['responses'],
        )


    def patch(self , request):
        phone = request.data.get("phone")
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')
        email = request.data.get('email')
        # check for the phone
        if not phone :
            return Response(data={"detail" : "phone number and password are missing"} , status=status.HTTP_400_BAD_REQUEST)

        # check for user
        try :
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return Response(data={"detail" : "user does not exists"} , status=status.HTTP_404_NOT_FOUND)

        # for password change
        if password and confirm_password :
            if password != confirm_password:
                return Response(data={"detail": "password must match"}, status=status.HTTP_400_BAD_REQUEST)
            try :
                validate_password(password)
            except ValidationError as e:
                raise rest_validation_error(e.messages)
            else :
                user = User.objects.get(phone=phone)
                user.set_password(password)




        # for email change
        if email :
            try :
                validate_email(email)
            except ValidationError as e:
                raise rest_validation_error(e.messages)
            else :
                user.email = email

        user.save()
        return Response(data={"detail": "Credentials updated successfully"}, status=status.HTTP_200_OK)



# to get the otp 
class GetOtp(APIView) :

    @swagger_auto_schema(
            operation_summary=docs.get_otp_document['operation_summary'],
            operation_description=docs.get_otp_document['operation_description'],
            manual_parameters=docs.get_otp_document['manual_parameters'],
            responses=docs.verify_otp_document['responses'],
            )

    def get(self , request):
        phone = request.GET.get('phone')
        # pattern = r"^09\d{9}$"
        # check for phone
        if not phone:
            return Response(data={"detail" : "phone number is not valid"} , status=status.HTTP_400_BAD_REQUEST)
        # check that user can request otp or not
        if can_request_otp(phone) :
            otp = create_otp(phone)
            return Response(data={"otp_sent" : True , "otp" : otp} , status=status.HTTP_200_OK)
        return Response(data={"detail" : f"try later"} , status=status.HTTP_400_BAD_REQUEST)



# signin/up the user with otp verification
class VerifyOtp(APIView) :
    @swagger_auto_schema(
        operation_description=docs.verify_otp_document['operation_description'],
        operation_summary=docs.verify_otp_document['operation_summary'],
        request_body=docs.verify_otp_document['request_body'],
        responses=docs.verify_otp_document['responses'],
    )
    def post(self , request):
        phone = request.data.get('phone')
        otp = request.data.get('otp')

        if not phone :
            return Response(data={"detail" : "phone number is missing"} , status=status.HTTP_400_BAD_REQUEST)
        if not otp :
            return Response(data={"detail" : "otp is missing"} , status=status.HTTP_400_BAD_REQUEST)
        # verify the otp that user sent
        verify = verify_otp(phone , otp)
        # check if otp is verified
        if verify == True:
            # creat token for user
            if user_have_account(phone) :
                tokens = create_tokens(phone)
                return Response(data={"user_exist" : True , "otp_valid" : True , "tokens" : tokens} , status=status.HTTP_200_OK)
            # create the user and create token
            else :
                user = User.objects.create_user(phone=phone)
                tokens = create_tokens(phone)
                return Response(data={"user_exist" : False , "otp_valid" : True , "tokens" : tokens} , status=status.HTTP_200_OK)
        else :
            return Response(data={"detail": f"{verify}"}, status=status.HTTP_400_BAD_REQUEST)





class ShowData(APIView) :
    permission_classes = [IsAdminUser]
    def get(self, request):
        return Response(data={"data": "Authorization"}, status=status.HTTP_200_OK)



# the second login

