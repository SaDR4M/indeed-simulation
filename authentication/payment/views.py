from django.shortcuts import render
# third party imports
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from django.db import transaction
from .models import Payment
from employer.models import EmployerCart
from celery.result import AsyncResult
from drf_yasg import openapi
# local imports
from .serializers import PaymentSerializer
from employer.models import Employer
from employer.utils import employer_exists
from . import utils
from .utils import verify_payment
from . import tasks
from employer.models import EmployerCart , EmployerOrder , EmployerCartItem , EmployerOrderItem
from employer.serializers import OrderSerializer , OrderItemSerializer
from account.models import Message
from account.tasks import send_order_sms ,  send_order_email
from guardian.shortcuts import assign_perm

# Create your views here.



class PaymentProcess(APIView) :
    @swagger_auto_schema(
        operation_summary="create payment link to purchase",
        operation_description="create payment link to purchase , create order and payment for the user",
        responses= {
            200 : openapi.Response(
                description="successfull",
                examples={
                    "application/json" : {
                        "success" : True,
                        "payment_url" : "payment url"
                    }
                }
                ),
        }
    )
    def get(self , request) :
        user = request.user
        employer = employer_exists(user)
        if not employer:
            return Response(data={"detail": "employer does not exists"}, status=status.HTTP_400_BAD_REQUEST)
        # check if there is pending payment do not allow user to create payment again
        acitve_payment = Payment.objects.filter(employer=employer , status="pending")
        if acitve_payment.exists() :
            return Response(data={"success" : False , "error" : "there is active payment for you" , "fa_error" : "پرداختی فعالی برای شما وجود دارد"} , status=status.HTTP_400_BAD_REQUEST)
        # save the payment
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid() :
            # using transaction atomic to be sure all data will save or nothing
            with transaction.atomic():
                # get the total amount of basket 
                amount = utils.calc_order_amount(employer)
                if amount is None :
                    return Response(data={"success" : False , "error" : "cart is empty" , "fa_error" : "سبد خرید خالی است"} , status=status.HTTP_400_BAD_REQUEST)
                # create the authority
                authority = utils.get_authority(amount)
                if authority is None:
                    return Response(data={"error" : "process failed" , "fa_error" : "مشکلی در پرداخت به وجود آمده"} , status=status.HTTP_400_BAD_REQUEST)
                # create the payment url
                url = utils.payment_link(authority)
                print(amount)
                payment_id = utils.create_random_number()
                payment = serializer.save(employer=employer , amount=amount , authority=authority , payment_id=payment_id)
                assign_perm("view_payment" , user , payment)
    
                # create order and order item base on the items in the employer cart and if the payment is successfull the cart status will be False
                # get the items in the cart
                # TODO optimize the query with prefetch related
                try :
                    cart = EmployerCart.objects.get(employer=employer , active=True)
                except EmployerCart.DoesNotExist :
                    return Response(data={"detail" : "cart is empty"} , status=status.HTTP_404_NOT_FOUND)
                # items in the active cart that will be order
                items = cart.cart_items.all()
                if not items :
                    return Response(data={"detail" : "cart is empty"} , status=status.HTTP_404_NOT_FOUND)
 
                # create the order
                order_serializer = OrderSerializer(data=request.data)
                if not order_serializer.is_valid():
                    return Response({"errors": order_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                
                # convert data to a list
                order_items_data = [
                    {
                        "package": item.package.id,
                    }
                    for item in items
                ]

                item_serializer = OrderItemSerializer(data=order_items_data, many=True)
                if not item_serializer.is_valid():
                    return Response({"errors": item_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                # deactivate the Cart and saving the data
                order_id = utils.create_random_number()
                order = order_serializer.save(employer=employer , order_id = order_id , payment=payment)
                assign_perm("view_employerorder" , user , order)
                item_serializer.save(order=order)
                cart.active = False
                cart.save()
                
                # cancel the payment if after 15 mintues payment was not successful
                # wait to transcation be done then check the        
                
                tasks.fail_payment_if_unpaid.apply_async(args=[payment.pk])
                # result = AsyncResult()
            return Response(data={"success": True , "payment_url" : url}, status=status.HTTP_200_OK)
        return Response(data={"success" : False , "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    

    @swagger_auto_schema(
        operation_summary="verify the pending payment status",
        operation_description="verify the user payment and return the status of the payment",
        responses= {
            200 : "success",
            400 : "invalid parameters",    
        }
    )
    def post(self , request):
        user = request.user
        employer = employer_exists(user)
        if not employer:
            return Response(data={"detail": "employer does not exists"}, status=status.HTTP_400_BAD_REQUEST)
        # get the current pending payment
        try :
            user_pending_payment = Payment.objects.get(employer=employer , status="pending")
        except Payment.DoesNotExist:
            return Response(data={"success": False , "error" : "payment does not exists" , "fa_error" : "پرداختی با این مشخصات وجود ندارد" } , status=status.HTTP_404_NOT_FOUND)

        authority = user_pending_payment.authority
        amount = user_pending_payment.amount
        # if the purchase was failed
        if not verify_payment(authority, amount):
            # user_pending_payment.status = "failed"
            user_pending_payment.save()
            return Response(data={"error" : "payment failed" , "fa_error" : "پرداخت ناموفق "}, status=status.HTTP_400_BAD_REQUEST)
            # if it was successful
        # user_pending_payment.status = "completed"
        # user_pending_payment.save()
        return Response(data={"success" : True , "fa_data" : "پرداخت موفق"} , status=status.HTTP_200_OK)



class Test(APIView):
    
    def get(self , request) :

        return Response(status=status.HTTP_200_OK)