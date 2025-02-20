
from rest_framework import serializers
from .models import User
# django & rest imports
from rest_framework.serializers import ModelSerializer
# third party imports
# local imports
from account.models import UserLog


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

class UserSimpleSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'mobile', 'name', 'family_name', 'is_active', 'is_real']
        
class UserLogSerializerBRF(ModelSerializer):
    class Meta:
        model = UserLog
        fields = "__all__"   
           
class UserProfileCompletionSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"     
              
class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {
                'write_only': True,
            },
            'temp_password': {
                'write_only': True,
            }
        }
