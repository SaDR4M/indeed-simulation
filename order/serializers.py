# third party imports
from rest_framework import serializers

# local import
from employer.models import Employer
from order.models import CartItem , OrderItem , Order , Cart
from package.models import Package
     

class CartItemSerializer(serializers.ModelSerializer) :
    # package = serializers.PrimaryKeyRelatedField(queryset=Package.objects.all())
    class Meta :
        model = CartItem
        exclude = ['cart' , 'package']

class CartSerializer(serializers.ModelSerializer) :
    class Meta :
        model = Cart
        exclude = ['employer']
        
class OrderSerializer(serializers.ModelSerializer) :
    class Meta :
        model = Order
        exclude = ['employer' , 'order_id' ,'payment']

class OrderItemSerializer(serializers.ModelSerializer) :
    package = serializers.PrimaryKeyRelatedField(queryset=Package.objects.all())
    class Meta:
        model = OrderItem
        exclude = ['order']

