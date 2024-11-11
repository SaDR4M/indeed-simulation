from django.db import models
# local import
# from payment.models import Payment
from django.contrib.auth import get_user_model

from authentication.employer.models import Employer

# Create your models here.
Payment = get_user_model()
Employer = get_user_model()

class Package(models.Model) :

    class PackagePriority(models.IntegerChoices):
        NORMAL = 0 , 'normal'
        URGENT = 1 , 'urgent'

    class PackageType(models.IntegerChoices):
        OFFER = 0 , 'offer'
        RESUME = 1 , 'resume'

    employer = models.ForeignKey(Employer , on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment , on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2 , default=100000.00)
    count = models.IntegerField(default=1)
    remaining = models.IntegerField(default=0)
    priority = models.IntegerField(choices=PackagePriority.choices, default=PackagePriority.NORMAL)
    type = models.IntegerField(choices=PackageType.choices, null=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

