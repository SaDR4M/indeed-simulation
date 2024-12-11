from django.urls import path

# local imports
from . import views

urlpatterns = [
    path('create-package/' , views.CreatePackage.as_view() , name="create-package"),
    path('purchase/' , views.PurchasePackage.as_view() , name="buy-package"),
    path('all-packages/' , views.AllPackage.as_view() , name="all_packages")
]
