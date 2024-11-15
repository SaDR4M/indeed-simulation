
from django.db import models

# local import
from employer.models import Employer


# Create your models here.
class Payment(models.Model):
    
    total_price = models.DecimalField(max_digits=10 , decimal_places=2)
    checkout_at = models.DateTimeField(auto_now_add=True)
    employer = models.ForeignKey(Employer , on_delete=models.CASCADE)







