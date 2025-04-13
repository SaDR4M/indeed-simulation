from django.db import models
from django.contrib.auth import get_user_model
# local import

from employer.models import Employer
from payment.models import Payment
from account.models import User
# Create your models here.

# packages that admins make for employers

class Package(models.Model) : 
    class PackagePriority(models.TextChoices):
        NORMAL = 'normal' , 'Normal'
        URGENT = 'urgent' , 'Urgent'

    class PackageType(models.TextChoices):
        OFFER = 'offer' , 'Offer'
        RESUME = 'resume' , 'Resume'

    user = models.ForeignKey(User , on_delete=models.CASCADE , related_name="packages")   
    price = models.DecimalField(max_digits=10, decimal_places=3)
    count = models.IntegerField()
    priority = models.CharField(choices=PackagePriority.choices, default=PackagePriority.NORMAL)
    type = models.CharField(choices=PackageType.choices, null=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(blank=True, null=True)



class PurchasedPackage(models.Model) : 
    package = models.ForeignKey(Package , on_delete=models.CASCADE , related_name="purchases")
    employer = models.ForeignKey(Employer , on_delete=models.CASCADE , related_name="packages")
    # payment = models.ForeignKey(Payment , on_delete=models.CASCADE)
    remaining = models.IntegerField()
    bought_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    
    
    def save(self , *args , **kwargs) :
        if self.pk is None :
            self.remaining = self.package.count
            # if self.package.type == "offer" :
            #     self.price = self.package.price
            # if self.package.type == "resume" :
            #     self.price = self.package.price * self.package.count
        super().save(*args , **kwargs)
    
 