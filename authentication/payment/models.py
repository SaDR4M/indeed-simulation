
from django.db import models
from django.contrib.auth import get_user_model
# local import
# from package.models import Package
Package = get_user_model()



# Create your models here.
class Payment(models.Model):
    package = models.ForeignKey(Package , on_delete=models.CASCADE)
    checkout_at = models.DateTimeField()
    total_price = models.DecimalField(max_digits=10 , decimal_places=2)






