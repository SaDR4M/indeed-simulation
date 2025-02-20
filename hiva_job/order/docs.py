# third party
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
# local
from order.serializers import OrderSerializer , OrderItemSerializer , CartItemSerializer , CartSerializer


order_get_doc = swagger_auto_schema(
        operation_summary="get orders data of the employer",
        operation_description="get the list of orders ",
        manual_parameters=[            
        openapi.Parameter(name='order_at' , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the orders with EXACT order_at date "),
        openapi.Parameter(name='min_order_at' , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the orders with MIN order_at date "),
        openapi.Parameter(name='max_order_at' , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the orders with MAX order_at date "),
        openapi.Parameter(name="price" , in_=openapi.IN_QUERY , type=openapi.TYPE_NUMBER , description="get the orders with EXACT package price (for having range price you must define max and min price together)"),
        openapi.Parameter(name="min_price" , in_=openapi.IN_QUERY , type=openapi.TYPE_NUMBER , description="get the orders with MIN package price (lte)"),
        openapi.Parameter(name="max_price" , in_=openapi.IN_QUERY , type=openapi.TYPE_NUMBER , description="get the orders with MAX package price (gte)"),
        openapi.Parameter(name="active" , in_=openapi.IN_QUERY , type=openapi.TYPE_BOOLEAN , description="get the orders with EXACT package type . options are True , False"),
        openapi.Parameter(name="count" , in_=openapi.IN_QUERY , type=openapi.TYPE_INTEGER , description="get the orders with EXACT package count"),
        openapi.Parameter(name="type" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the orders with EXACT package type. options are : 'offer' , 'resume' "),
        openapi.Parameter(name="priority" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the orders with EXACT package priority. options are : 'normal' , 'urgent' "),
        openapi.Parameter(name="created_at" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING, description="get the orders with this EXACT package created date time (for having range date time you must define max and min created date time together)"),
        openapi.Parameter(name="min_created_at" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the orders with MIN package created date time (lte)"),
        openapi.Parameter(name="max_created_at" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the orders with MAX package created date time (gte)"),
        openapi.Parameter(name="deleted_at" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING, description="get the orders with this EXACT package deleted date time (for having range date time you must define max and min deleted date time together)"),
        openapi.Parameter(name="min_deleted_at" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the orders with MIN package deleted date time (lte)"),
        openapi.Parameter(name="max_deleted_at" , in_=openapi.IN_QUERY , type=openapi.TYPE_STRING , description="get the orders with MAX package deleted date time  (gte)"),
        ],
        responses={
            200: OrderSerializer,
            404: "employer/order was not found",
            403: "user doesn't have permission to change this data",
        },
        security=[{"Bearer": []}]
    )

order_item_get_doc = swagger_auto_schema(
        operation_summary="get the data of order items",
        operation_description="get the data of order items if order/order items exists",
        responses={
            200: OrderItemSerializer,
            400: "invalid parameters",
            404: "employer/order/order item was not found",
            403: "user doesn't have permission to change this data",
        },
        security=[{"Bearer": []}]
    )


cart_get_doc = swagger_auto_schema(
        operation_summary="get the employer cart",
        operation_description="get the cart information of the employer and if there is no cart for this user a active cart will be created",
        responses={
            200 : CartSerializer,
            404 : "employer cart was not found",
            403 : "user doesn't have permission to change this data",
        },
        security=[{"Bearer" : []}]
    )

cart_delete_doc = swagger_auto_schema(
        operation_summary="deactivate the employer cart",
        operation_description="deactivate the employer cart",
        responses={
            200 : "successfully",
            404 : "employer/active cart was not found",
            403 : "user doesn't have permission to change this data",
        },
        security=[{"Bearer" : []}]
    )

cart_item_get_doc = swagger_auto_schema(
        operation_summary="get the employer cart items",
        operation_description="get the cart items for the active cart of the employer",
        responses={
            200: CartItemSerializer,
            404: "employer/active cart was not found",
            403: "user doesn't have permission to change this data",
        },
        security=[{"Bearer": []}]
    )

cart_item_post_doc = swagger_auto_schema(
        operation_summary="add cart items to employer active cart",
        operation_description="if there is active cart for the employer add the package to it and if not create the cart then add the package",
        request_body = openapi.Schema(type=openapi.TYPE_OBJECT,properties={"package_id" : openapi.Schema(type=openapi.TYPE_STRING, description="package id")} , required=['package_id']),
        responses={
            200: "successfully",
            400: "invalid parameters",
            404: "employer/active cart was not found",
            403: "user doesn't have permission to change this data",
        },
        security=[{"Bearer": []}]
    )

cart_item_delete_doc = swagger_auto_schema(
        operation_summary="delete the item from cart",
        operation_description="delete a specific item from a cart",
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            "item_id": openapi.Schema(type=openapi.TYPE_STRING, description="item id")}, required=['package_id']),
        responses={
            200: "successfully",
            400: "invalid parameters",
            404: "employer/item was not found",
            403: "user doesn't have permission to change this data",
        },
        security=[{"Bearer": []}]
    )