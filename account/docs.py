# third party imports
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

USER_ROLE = "0 : pre register , 1 : employer , 2 : job seeker , 3 : operator , 10 : admin"
otp_document = swagger_auto_schema(
        operation_description="Sending OTP to the user mobile",
        operation_summary="Sending OTP",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "mobile" : openapi.Schema(description="user mobile" , type=openapi.TYPE_STRING , minlength=11)
                # "with_call" : 
            },
            required=["mobile"]
        ),
        responses={
            200 : "OTP is sent to the user",
            400 : "Wrong mobile number format"
        },
        security = [{"Bearer": []}]
    )


sign_up_document = swagger_auto_schema(
        operation_description="Checking the OTP that was sent to user with the entered OTP then Signup the user",
        operation_summary="Signup",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "mobile" : openapi.Schema(description="user mobile" , type=openapi.TYPE_STRING , minlength=11),
                "otp" : openapi.Schema(description="otp" , type=openapi.TYPE_STRING , minlength=5),
                "birthday" : openapi.Schema(description="user birthday" , type=openapi.TYPE_STRING),
                "password" : openapi.Schema(description="user password" , type=openapi.TYPE_STRING),
                "role" : openapi.Schema(description=USER_ROLE , type=openapi.TYPE_STRING)
            },
            required=["mobile" , "role" , "otp" , "birthday" , "password"]
        ),

        responses={
            200: openapi.Response(
            description="user is logged in or signed up",
            examples={
                "application/json": {
                    "succeeded": True,
                    "Authorization" : "Access token",
                    "role" : 10
                    }
                }
            ),
            400 : "Wrong OTP or OTP is expired - invalid paramters"
        },
        security = [{"Bearer": []}]
    )


sign_in_otp_document = swagger_auto_schema(
        operation_description="Checking the OTP that was sent to user with the entered OTP then Signin the user",
        operation_summary="Signin with OTP",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "mobile" : openapi.Schema(description="user mobile" , type=openapi.TYPE_STRING , minlength=11),
                "otp" : openapi.Schema(description="otp" , type=openapi.TYPE_STRING , minlength=5),
                "role" : openapi.Schema(description=USER_ROLE , type=openapi.TYPE_STRING , minlength=5)
            },
            required=["mobile" , "role" , "otp"]
        ),

        responses={
            200: openapi.Response(
            description="user is logged in or signed up",
            examples={
                "application/json": {
                    "succeeded": True,
                    "Authorization" : "Access token",
                    "role" : 10
                    }
                }
            ),
            400 : "Wrong OTP or OTP is expired"
        },
        security = [{"Bearer": []}]
    )


sign_in_pass_document = swagger_auto_schema(
            operation_summary="Signin with password",
            operation_description = "Sign in with phone number and password",
            request_body = openapi.Schema(
                type = openapi.TYPE_OBJECT,
                properties = {
                    'mobile' : openapi.Schema(type=openapi.TYPE_STRING, description="mobile number" , minLength=11 , title="Phone"),
                    'password' : openapi.Schema(type=openapi.TYPE_STRING, description="password" , minlength=8 , title="Password"),
                    'role' : openapi.Schema(type=openapi.TYPE_STRING , description=USER_ROLE , minlength=5 , title="Role")
                },
                required = ['mobile','role','password'],
            ),
            responses = {

                201 : openapi.Response(
                    description='token created successfully' ,
                    examples={
                        "application/json": {  # Specify MIME type to clarify format
                            "succeeded" : True,
                            "Token": "string",
                        }
                    }
                    ),
                400 : 'invalid parameters',
            },
            security = [{"Bearer": []}]
)

update_credential_document = swagger_auto_schema(
    operation_summary = "Update user password",
    operation_description = "Update user password.the password must be at least 8 char and combination of characters and numbers",
    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            # 'email': openapi.Schema(description="user email address", type=openapi.TYPE_STRING, example="test@gmail.com",
            #                         format="email"),
            'old_password' : openapi.Schema(
                description="user's old password" , type=openapi.TYPE_STRING, minlenght=8),
            'new_password': openapi.Schema(
                description="new password for the user", type=openapi.TYPE_STRING, minlength=8,format="password"),
            'confirm_password': openapi.Schema(
                description="confirm the new password", minlength=8,type=openapi. TYPE_STRING),
            
        },
        required=['old_password' , 'new_password' , 'confirm_password']
    ),
    responses = {
        200: openapi.Response(
            description="information updated successfully",
            examples={
                "application/json": {
                    "succeeded" : True,
                    "show" : True,
                    "en_detail" : "password changed successfully",
                    "fa_detail" : "پسورد با موفقیت تغییر کرد"
                }
            }),
        400: openapi.Response(description="invalid credentials"),
    },
    security = [{"Bearer": []}]
)