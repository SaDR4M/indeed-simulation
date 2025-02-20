from django.db import models

# Create your models here.
# basket package


class Order(models.Model) :
    
    class OrderStatus(models.TextChoices) :
        COMPLETED = "completed"
        PENDING = "pending"
        FAILED = "failed"
        REFUNDED = "refunded"
        
    employer = models.ForeignKey("employer.Employer" , on_delete=models.CASCADE , related_name="orders")
    payment = models.OneToOneField("payment.Payment" , on_delete=models.CASCADE , related_name="order")
    status = models.CharField(choices=OrderStatus , default=OrderStatus.PENDING)
    order_at = models.DateTimeField(auto_now_add=True)
    order_id = models.IntegerField()

class OrderItem(models.Model) :
    order = models.ForeignKey(Order , on_delete=models.CASCADE , related_name="order_items")
    package = models.ForeignKey("package.Package" , on_delete=models.CASCADE , related_name="packages")
    added_at = models.DateTimeField(auto_now_add=True)