from django.urls import path , re_path
# from . import consumers
# local imports
from . import views
urlpatterns = [
    # path('create-payment/' , views.CreatePayment.as_view() , name="create-payment"),
    path('purchase/' , views.PaymentProcess.as_view() , name="purchase"),
    path('payment/', views.Payments.as_view() , name="payments")
    # path('request/', views.send_request, name='request'),
    # path('verify/', views.verify, name='verify'),
]
# websocket_urlpatterns = [
#     re_path(r"ws/notifications/$", consumers.NotificationConsumer.as_asgi()),
# ]