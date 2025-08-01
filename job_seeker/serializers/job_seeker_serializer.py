# third party imports
from rest_framework import serializers
from icecream import ic
# local imports
from job_seeker.models import JobSeeker
from location.models import Cities , Provinces
from location.serializer import CitiesSerializer , ProvincesSerializer
from job_seeker.serializers.resume_serializer import GetResumeSerializer
from account.serializer import UserSimpleSerializer

class JobSeekerSerializer(serializers.ModelSerializer):
    class Meta :
        model = JobSeeker
        exclude = ['user' , 'city' , 'province']
        # fields = '__all__'
        
        
class UpdateJobSeekerSerializer(serializers.ModelSerializer) :
    province_id = serializers.IntegerField(required=False)
    city_id = serializers.IntegerField(required=False)
    email = serializers.EmailField(required=False)
    class Meta :
        model = JobSeeker
        exclude = ['user' , 'city' , 'province']     
        
    def update(self , instance , validated_data) : 
        try :
            city = validated_data.get("city_id")
            province = validated_data.get("province_id")
            instance.city = Cities.objects.get(id=city , province_id = province)
        except : 
            pass
        try :
            province = validated_data.get("province_id")
            instance.province = Provinces.objects.get(id=province)
        except :
            pass
        try :
            email = validated_data.get("email")
            instance.user.email = email
            instance.user.save()
        except :
            pass
        super().update(instance , validated_data)
        return instance
    
    
class JobSeekerDataSerialzier(serializers.ModelSerializer) :
    user = UserSimpleSerializer()
    city = CitiesSerializer()
    province = ProvincesSerializer()
    resume = GetResumeSerializer()
    class Meta:
        model = JobSeeker
        fields = '__all__'
