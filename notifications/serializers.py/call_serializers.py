# django & rest imports
from rest_framework.serializers import ModelSerializer
# local imports
from authentication.account.serializers import UserSimpleSerializer
from notifications.models import CallLog , CallCategory 


class CallLogShowSerializer(ModelSerializer):
    call_by = UserSimpleSerializer()

    class Meta:
        model = CallLog
        fields = "__all__"


class CallCatgorySerializer(ModelSerializer):
    class Meta:
        model = CallCategory
        fields = "__all__"

class CallLogSerializer(ModelSerializer):
    class Meta:
        model = CallLog
        fields = "__all__"
        
class CallLogShowSerializer(ModelSerializer):
    smsCat = CallLogSerializer()
    class Meta:
        model = CallLog
        fields = "__all__"
