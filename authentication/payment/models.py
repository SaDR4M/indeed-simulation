from django.db import models
# local import
from authentication.package.models import Package





# Create your models here.
class Payment(models.Model):
    package = models.ForeignKey(Package , on_delete=models.CASCADE)
    checkout_at = models.DateTimeField()
    total_price = models.DecimalField(max_digits=10 , decimal_places=2)






