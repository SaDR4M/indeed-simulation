from rest_framework.serializers import ModelSerializer
from authentication.account.serializers import UserProfileInfoSerializer
from notifications.models import SMSLog , SmsCategory , ReceivedSms


class SMSLogShowSerializer(ModelSerializer):
    send_by = UserProfileInfoSerializer()

    class Meta:
        model = SMSLog
        fields = "__all__"

class SmsCategorySerializer(ModelSerializer):
    class Meta:
        model = SmsCategory
        fields = "__all__"

class SMSLogSerializer(ModelSerializer):
    class Meta:
        model = SMSLog
        fields = "__all__"
        
class SMSLogShowSerializer(ModelSerializer):
    smsCat = SmsCategorySerializer()
    class Meta:
        model = SMSLog
        fields = "__all__"

class ReceivedSmsSerializer(ModelSerializer):
    class Meta:
        model = ReceivedSms
        fields = "__all__"
