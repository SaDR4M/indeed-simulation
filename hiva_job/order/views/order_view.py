import datetime
from dataclasses import dataclass


# tdjango & rest 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK , HTTP_400_BAD_REQUEST , HTTP_404_NOT_FOUND
# third party
from package.serializers import PackageSerializer
# local
from order.serializers import (
    OrderSerializer, OrderItemSerializer
            )       
from order.models import Order 
from order.mixins import FilterOrderMixin 
from order.docs import order_get_doc , order_item_get_doc
from employer.utils import employer_exists
# Create your views here.




class Order(APIView , FilterOrderMixin) :
    # list of the order by the user
    @order_get_doc
    def get(self, request):
        """user's orders"""
        user = request.user
        employer = employer_exists(user)
        
        if not employer:
            return Response(data={"detail": "Employer does not exist"}, status=HTTP_404_NOT_FOUND)
        # using prefetch cause we want to get all the order items and package datas we use it to decrease the querie
        employer_orders = Order.objects.filter(employer=employer)

        filtered_orders = self.filter_order(employer_orders)
        if isinstance(filtered_orders , Response) :
            return filtered_orders
        
        orders = filtered_orders.prefetch_related(
            'order_items__package'  #
        ).order_by('order_at')
        
        # serialize the orders
        data = []
        for order in orders:

            order_data = OrderSerializer(order).data
            
            order_items_data = []
            for item in order.order_items.all():  # 
                order_item_data = OrderItemSerializer(item).data
            
                package_data = PackageSerializer(item.package).data
                order_item_data['package'] = package_data
                
                order_items_data.append(order_item_data)
            order_data['items'] = order_items_data
            data.append(order_data)
        
        return Response(data={"data": data}, status=HTTP_200_OK)


class OrderItem(APIView) :
    # list of the order items
    @order_item_get_doc
    def get(self , request):
        """specific order items"""
        user = request.user
        employer = employer_exists(user)
        order_id = request.data.get('order_id')
        if not order_id :
            return Response(data={"detail" : "order_id must be entered"} , status=HTTP_400_BAD_REQUEST)
        if not employer :
            return Response(data={"detail" : "employer does not exists"} , status=HTTP_404_NOT_FOUND)
        try :
            order = Order.objects.get(pk=order_id , employer=employer)
        except Order.DoesNotExist :
            return Response(data={"detail" : "order does not exists"} , status=HTTP_404_NOT_FOUND)
        order_items = order.order_items.all()
        if not order_items :
            return Response(data={"detail" : "there is no item for this order"} , status=HTTP_404_NOT_FOUND)
        serializer = OrderItemSerializer(order_items , many=True)
        return Response(data={"data" : serializer.data} , status=HTTP_200_OK)