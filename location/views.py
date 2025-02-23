# django & rest 
from rest_framework.views import APIView
from rest_framework.response import Response 
from rest_framework.status import HTTP_200_OK , HTTP_400_BAD_REQUEST
# local 
from location.models import Cities , Provinces
from location.serializer import CitiesSerializer , ProvincesSerializer
# Create your views here.

class ListOfProvinces(APIView) :
    def get(self , request) :
        provinces = Provinces.objects.all()
        serializer = ProvincesSerializer(provinces , many=True)
        return Response(
                data = serializer.data,
                status = HTTP_200_OK
        )


class ListOfCities(APIView) :
    def get(self , request) :
        cities = Cities.objects.all()
        serializer = CitiesSerializer(cities , many=True)
        return Response(
                data = serializer.data,
                status = HTTP_200_OK
        )


class ListOfProvinceCities(APIView) :
    def get(self , request) :
        province = request.data.get("province_id")
        
        if not province :
            return Response(
                data = {"en_detail" : "province must be entered"},
                status = HTTP_200_OK
            )
        
        cities = Cities.objects.filter(province_id = province)
        serializer = CitiesSerializer(cities , many=True)
        return Response(
            data = serializer.data,
            status = HTTP_200_OK
        )