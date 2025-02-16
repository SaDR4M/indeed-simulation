from django.urls import path

# local imports
from . import views

urlpatterns = [

    path('purchase/' , views.PurchasePackage.as_view() , name="buy-package"),

]
