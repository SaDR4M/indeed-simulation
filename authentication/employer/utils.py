# third party imports


# local imports
from struct import pack
from package.models import PurchasedPackage
from job_seeker.models import Application
from employer.models import Employer
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
    if purchased.package.type == 1 :
        return False
    remaining = purchased.remaining
    if remaining == 0 :
        return False
    purchased.remaining -= 1
    purchased.save()
    return True


# check the count of the resume sent for the user base on the package they bought and limit the response
def count_of_resume_to_check(employer) :
    # employer packages with type of 1 (resume)
    total = 0
    purchased_packages = PurchasedPackage.objects.filter(employer=employer ,package__type=1)
    for package in purchased_packages.all() :
        total += package.remaining
    return int(total)