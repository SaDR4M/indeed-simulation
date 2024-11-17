# third party imports


# local imports
from package.models import PurchasedPackage



# can not make job opportunity if they do not have any packages
def can_create_offer(employer , package_purchase_id) : 
    purchased = PurchasedPackage.objects.filter(employer=employer ,  pk=package_purchase_id , active=True)
    if purchased.exists() :
        return True
    return False



# can not make job opportunity if their package is 0 ( not active) => when the user
def check_package_remaining(employer , package_purchase_id)   :
    try : 
        purchased = PurchasedPackage.objects.get(employer=employer , pk=package_purchase_id)
    except PurchasedPackage.DoesNotExist :
        return False
    remaining = purchased.remaining
    if remaining == 0 :
        return False
    purchased.remaining -= 1
    purchased.save()
    return True


# calc the total price and update it