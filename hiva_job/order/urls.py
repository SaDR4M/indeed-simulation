from django.urls import path
from . import views

path('cart/' , views.Cart.as_view() , name="cart"),
path('cart-items/' , views.Cartitems.as_view() , name="cart_items"),
path('order/' , views.Order.as_view() , name="order"),
path('order-items/' , views.OrderItem.as_view() , name="order_items"),