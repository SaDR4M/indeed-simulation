from django.db import models


class Cart(models.Model) :
    employer =  models.ForeignKey("employer.Employer" , on_delete=models.CASCADE ,  related_name="carts")
    active = models.BooleanField(default=True)
    added_at = models.DateTimeField(auto_now_add=True)
    
class CartItem(models.Model) :
    cart = models.ForeignKey(Cart  , on_delete=models.CASCADE , related_name="cart_items")
    package = models.ForeignKey("package.Package" , on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)