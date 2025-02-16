# third party imports
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema






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