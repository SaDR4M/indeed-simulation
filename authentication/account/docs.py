from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


# function that return the document


sign_in_document = {
            "operation_summary" : "Sign in",
            "operation_description" : "Sign in with phone number and password",
            "request_body" : openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'phone' : openapi.Schema(type=openapi.TYPE_STRING, description="phone number" , minLength=11 , title="Phone"),
                    'password' : openapi.Schema(type=openapi.TYPE_STRING, description="password" , minlength=8 , title="Password"),
                },
                required=['phone','password'],
            ),
            "responses" : {

                201 : openapi.Response(
                    description='token created successfully' ,
                    examples={
                        "application/json": {  # Specify MIME type to clarify format
                            "tokens": {
                                "access": "string",
                                "refresh": "string"
                            }
                        }
                    }
                    ),
                400 : 'invalid parameters',
                404 : 'user not found',
            }
}

update_credential_document = {
    "operation_summary" : "update user information",
    "operation_description" : "Update user information with the user phone number , the password must be at least 8 char and combination of characters and numbers",
    "request_body" : openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'phone': openapi.Schema(description="phone number", type=openapi.TYPE_STRING, minlength=11,
                                    example='091212345678'),
            'email': openapi.Schema(description="user email address", type=openapi.TYPE_STRING, example="test@gmail.com",
                                    format="email"),
            'password': openapi.Schema(description="new password for the user", type=openapi.TYPE_STRING, minlength=8,
                                       format="password"),
            'confirm_password': openapi.Schema(description="confirm the new password", minlength=8,
                                               type=openapi.TYPE_STRING),
        },
        required=['phone']
    ),
    "responses" : {
        200: openapi.Response(
            description="information updated successfully",
            examples={
                "application/json": {
                    "detail": "updated successfully",
                }
            }),
        400: openapi.Response(description="invalid credentials"),
        404: openapi.Response(description="user does not exists"),
    },
    "security" : [{"Bearer": []}]
}

get_otp_document = {
    "operation_summary" : "Get otp",
    "operation_description" : "Get the otp for the phone number",
    "manual_parameters" : [
        openapi.Parameter('phone', openapi.IN_QUERY, description="otp for the phone number", type=openapi.TYPE_STRING,
                          required=True, minlength=11)],
    "responses" : {
        200: openapi.Response(description="otp", examples={"application/json": [{"otp": "123456", "otp_sent": True}]}),
        400: "invalid parameters"
    }
}



verify_otp_document = {
    "operation_summary" : "verify otp",
    "operation_description" : "Verify the otp for the phone number",
    "request_body" : openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "phone": openapi.Schema(description="phone number", type=openapi.TYPE_STRING, minlength=11),
            "otp": openapi.Schema(description="otp", type=openapi.TYPE_STRING),
        },
        required=['phone' , 'otp']
    ),
    # "security" : [{"bearer": []}],
    "responses" : {
        200: openapi.Response(
            description="valid otp",
            examples={
                "application/json": {
                    "user_exist": True,
                    "otp_valid": True,
                    "tokens": {
                        "access": "string",
                        "refresh": "string",
                    }
                }
            }
        ),
        400: "invalid parameters",
    }
}