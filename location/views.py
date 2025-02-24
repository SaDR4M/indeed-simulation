# django & rest 
from rest_framework.views import APIView
from rest_framework.response import Response 
from rest_framework.status import HTTP_200_OK , HTTP_400_BAD_REQUEST
# local 
from location.models import Cities , Provinces
from location.serializer import CitiesSerializer , ProvincesSerializer
from location.docs import all_cities_get_doc, all_provinces_get_doc ,province_cities_get_doc
# Create your views here.

class ListOfProvinces(APIView) :
    
    @all_provinces_get_doc
    def get(self , request) :
        """list of all provinces"""
        provinces = Provinces.objects.all()
        serializer = ProvincesSerializer(provinces , many=True)
        return Response(
                data = serializer.data,
                status = HTTP_200_OK
        )


class ListOfCities(APIView) :
    
    @all_cities_get_doc
    def get(self , request) :
        """list of all cities"""
        cities = Cities.objects.all()
        serializer = CitiesSerializer(cities , many=True)
        return Response(
                data = serializer.data,
                status = HTTP_200_OK
        )


class ListOfProvinceCities(APIView) :
    
    @province_cities_get_doc
    def get(self , request) :
        """get list of cities for a province"""
        province = request.query_params.get("province_id")
        
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