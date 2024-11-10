from django.contrib.auth import authenticate
from django.db.migrations import serializer
from rest_framework import serializers
from .models import User
from django.core.exceptions import ValidationError

from .utils import verify_otp
#
#
#
# class SignUpSerializer(serializers.Serializer):
#
#     phone = serializers.CharField(required=True)
#     password = serializers.CharField(required=True)
#     password_confirm = serializers.CharField(required=True)
#
#     def validate_phone(self, phone):
#         if User.objects.filter(phone=phone).exists():
#             raise serializers.ValidationError("User exists")
#         return phone
#
#     def validate(self , attrs):
#         password = attrs.get('password')
#         password_confirm = attrs.get('password_confirm')
#         phone = attrs.get('phone')
#
#         if password != password_confirm:
#             raise serializers.ValidationError("Passwords do not match")
#         try :
#             validate_password(password)
#         except ValidationError as e:
#             raise serializers.ValidationError(e.messages)
#         return attrs
#
#
#

# class UpdateCredential(serializers.Serializer):
#     phone = serializers.CharField(max_length=11 , required=True)
#     password = serializers.CharField(required=False, write_only=True , allow_null=False)
#     password_confirm = serializers.CharField(required=False , allow_null=False)
#     email = serializers.EmailField(required=False)
#
#     def validate(self, attrs):
#         phone = attrs.get('phone')
#         password = attrs.get('password')
#         confirm_password = attrs.get('password_confirm')
#
#         if password != confirm_password:
#             raise serializers.ValidationError("passwords must match")
#         try :
#             user = User.objects.get(phone=phone)
#         except User.DoesNotExist:
#             raise serializers.ValidationError("user does not exist")
#         else :
#             try :
#                 validate_password(password)
#             except ValidationError as e:
#                 raise serializers.ValidationError(e.messages)
#         return attrs

class UpdateCredential(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['phone', 'password', 'confirm_password', 'email']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'phone': {'required': False},
            'email': {'required': False},
        }

    def validate(self, data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        if password and password != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def update(self, instance, validated_data):
        # Set and hash password if provided
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
