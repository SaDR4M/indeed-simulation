# django & rest 
from rest_framework.serializers import ModelSerializer
# local
from location.models import Cities , Provinces


class CitiesSerializer(ModelSerializer) :
    class Meta : 
        model = Cities
        fields = '__all__'

class ProvincesSerializer(ModelSerializer) :
    class Meta :
        model = Provinces
        fields = '__all__'
