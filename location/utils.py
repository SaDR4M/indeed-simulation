# django & drf 
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND
# local
from location.models import Provinces , Cities

def get_province(province_id:int) -> object:
    try :
        province = Provinces.objects.get(id = province_id)
    except Provinces.DoesNotExist :
        return Response(  
            data = {
                "en_detail" : "province does not exists"
            },
            status=HTTP_404_NOT_FOUND 
        )
    return province
    
def get_city(province_id:int , city_id:int) -> object :
    try :
        city = Cities.objects.get(id = city_id , province_id = province_id)
    except Cities.DoesNotExist :
        return Response(
            data = {
                "en_detail" : "city does not exists",
            },
            status=HTTP_404_NOT_FOUND
        )
    return city