from django.urls import path
# local
from location import views



urlpatterns = [
    path("all-provinces/" , views.ListOfProvinces.as_view() , name = "all_provinces"),
    path("all-cities/" , views.ListOfCities.as_view() , name="all_cities"),
    path("province-cities/" , views.ListOfProvinceCities.as_view() , name="province_cities")
]