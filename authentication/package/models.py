from django.db import models
from django.contrib.auth import get_user_model
# local import

from employer.models import Employer
from payment.models import Payment
from account.models import User
# Create your models here.

# packages that admins make for employers

class Package(models.Model) : 
    class PackagePriority(models.IntegerChoices):
        NORMAL = 0 , 'normal'
        URGENT = 1 , 'urgent'

    class PackageType(models.IntegerChoices):
        OFFER = 0 , 'offer'
        RESUME = 1 , 'resume'
    user = models.ForeignKey(User , on_delete=models.CASCADE , related_name="packages")   
    price = models.DecimalField(max_digits=10, decimal_places=2)
    count = models.IntegerField(default=1)
    priority = models.IntegerField(choices=PackagePriority.choices, default=PackagePriority.NORMAL)
    type = models.IntegerField(choices=PackageType.choices, null=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(blank=True, null=True)



class PurchasedPackage(models.Model) : 
    package = models.ForeignKey(Package , on_delete=models.CASCADE , related_name="purchases")
    employer = models.ForeignKey(Employer , on_delete=models.CASCADE , related_name="packages")
    payment = models.ForeignKey(Payment , on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # count = models.IntegerField(default=1)
    remaining = models.IntegerField(default=0)
    bought_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    
    def total_price(self) :
        total = self.package.price * self.package.count
        self.price = total
        return total
