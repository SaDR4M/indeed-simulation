
# django & rest imports
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK ,HTTP_400_BAD_REQUEST , HTTP_403_FORBIDDEN , HTTP_404_NOT_FOUND
from guardian.shortcuts import assign_perm
from package.serializers import PackageSerializer
# local imports
from order.serializers import (
                          CartSerializer,
                          CartItemSerializer,
                          )              
from order.models import Cart , CartItem 
from package.models import Package
from employer.utils import employer_exists
from order.docs import (
    cart_get_doc,
    cart_delete_doc,
    cart_item_get_doc,
    cart_item_post_doc,
    cart_item_delete_doc
)


class Cart(APIView) :
    # get the cart data
    @cart_get_doc
    def get(self , request):
        """list of user cart"""
        # add permission to view only their cart
        user = request.user
        employer = employer_exists(user)
        if not employer :
            return Response(data={"detail" : "employer does not exists"} , status=HTTP_404_NOT_FOUND)
        employer_cart = Cart.objects.filter(employer=employer , active = True)
        if not employer_cart.exists() :
            return Response(data={"data" : {}} , status=HTTP_404_NOT_FOUND)
        # check permission of the user
        if not user.has_perm("view_employecart" , employer_cart.first()) :
            return Response(status=HTTP_403_FORBIDDEN)
        serializer = CartSerializer(employer_cart , many=True)
        return Response(data={"data" : serializer.data} , status=HTTP_200_OK)



    # delete the cart virtually
    @cart_delete_doc
    def delete(self , request):
        """delete cart virtually"""
        user = request.user
        employer = employer_exists(user)
        if not employer :
            return Response(data={"detail" : "employer does not exists"} , status=HTTP_404_NOT_FOUND)
        employer_cart = Cart.objects.filter(employer = employer , active=True)
        if not employer_cart.exists() :
            return Response(data={"detail" : "there is no active cart for this user"} , status=HTTP_404_NOT_FOUND)
        # check permission of the user
        if not user.has_perm("delete_cart" , employer_cart.first()) :
            return Response(status=HTTP_403_FORBIDDEN)
        employer_cart.update(active = False)
        return Response(data={"detail" : "cart deleted successfully" , "success" : True} , status=HTTP_200_OK)

        

class Cartitems(APIView) :

    @cart_item_get_doc
    def get(self , request) :
        """view user's cart itmes"""
        user = request.user
        employer = employer_exists(user)
        if not employer :
            return Response(data={"detail" : "employer does not exists"} , status=HTTP_404_NOT_FOUND)

        try :
            employer_cart = Cart.objects.get(employer = employer , active = True)
        except Cart.DoesNotExist :
            # if there was no active cart
            return Response(data={"data" : {}}, status=HTTP_404_NOT_FOUND)
        
        # check user permission
        if not user.has_perm("view_cartitem" , employer_cart) :
            return Response(status=HTTP_403_FORBIDDEN)

        data = []
        cart_items = employer_cart.cart_items.all()
        for item in cart_items :
            cart_serializer = CartItemSerializer(item).data
            packages_serialzier = PackageSerializer(item.package).data
            cart_serializer['package'] = packages_serialzier
            data.append(cart_serializer)
        return Response(data={"data" : data} , status=HTTP_200_OK)



    @cart_item_post_doc
    def post(self , request) :
        """add item to user's cart"""
        user = request.user
        employer = employer_exists(user)
        package_id = request.data.get('package_id')
        if not package_id :
            return Response(data={"detail" : "package id must be entered"} , status=HTTP_400_BAD_REQUEST)
        if not employer :
            return Response(data={"detail" : "employer does not exists"} , status=HTTP_404_NOT_FOUND)
 
        employer_cart = Cart.objects.filter(employer=employer , active=True)
        if not employer_cart.exists() :
            # if there was no active cart create the cart
            serializer = CartSerializer(data=request.data)
            if serializer.is_valid():
                cart = serializer.save(employer=employer)
                assign_perm("view_cart" , user , cart )
                assign_perm("change_cart" , user , cart)
                assign_perm("delete_cart" , user , cart)
            else :
                return Response(data={"data": serializer.errors}, status=HTTP_400_BAD_REQUEST)

        try :
            package = Package.objects.get(pk=package_id , active=True)
        except Package.DoesNotExist :
            return Response(data={"detail" : "package does not exist"} , status=HTTP_404_NOT_FOUND)

        serializer = CartItemSerializer(data=request.data)

        if serializer.is_valid() :
            cart_item = serializer.save(cart=employer_cart.first() , package=package)
            assign_perm("view_cartitem" , user , cart_item)
            assign_perm("change_cartitem" , user , cart_item)
            assign_perm("delete_cartitem" , user , cart_item)
            return Response(data={"success" : True} , status=HTTP_200_OK)
        return Response(data={"errors" : serializer.errors} , status=HTTP_400_BAD_REQUEST)

    @cart_item_delete_doc
    def delete(self , request) :
        """delete item for user's cart"""
        user = request.user
        employer = employer_exists(user)
        item_id = request.data.get('item_id')
        if not item_id :
            return Response(data={"detail" : "item id must be entered"} , status=HTTP_400_BAD_REQUEST)
        if not employer :
            return Response(data={"detail" : "employer does not exists"} , status=HTTP_404_NOT_FOUND)

        try :
            cart_item = CartItem.objects.get(pk=item_id , cart__employer=employer)
        except CartItem.DoesNotExist :
            return Response(data={"detail" : "item does not exists"} , status=HTTP_404_NOT_FOUND)
        # check user permission
        if not user.has_perm("delete_cartitem" , cart_item) :
            return Response(status=HTTP_403_FORBIDDEN)
        cart_item.delete()
        return Response(data={"success" : True } , status=HTTP_200_OK)

