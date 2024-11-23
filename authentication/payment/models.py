
from django.db import models

# local import
from employer.models import Employer


# Create your models here.
class Payment(models.Model):
    class PaymentStatus(models.TextChoices) :
        PENDING = 'pending' , "Pending"
        COMPLETED = 'completed' , "Completed"
        FAILED = 'failed' , "Failed"
        REFUNDED = 'refunded' , "Refunded"
    
    employer = models.ForeignKey(Employer , on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10 , decimal_places=3)
    checkout_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=PaymentStatus , default=PaymentStatus.PENDING)







