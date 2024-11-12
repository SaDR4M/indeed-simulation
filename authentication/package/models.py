from django.db import models
from django.contrib.auth import get_user_model
# local import

from django.contrib.auth import get_user_model

Employer = get_user_model()
Payment = get_user_model()

# Create your models here.

# packages that admins make for employers
class Package(models.Model) :

    class PackagePriority(models.IntegerChoices):
        NORMAL = 0 , 'normal'
        URGENT = 1 , 'urgent'

    class PackageType(models.IntegerChoices):
        OFFER = 0 , 'offer'
        RESUME = 1 , 'resume'

    employer = models.ManyToManyField(Employer , related_name="employers")
    payment = models.ForeignKey(Payment , on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2 , default=100000.00)
    count = models.IntegerField(default=1)
    remaining = models.IntegerField(default=0)
    priority = models.IntegerField(choices=PackagePriority.choices, default=PackagePriority.NORMAL)
    type = models.IntegerField(choices=PackageType.choices, null=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

