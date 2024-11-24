import random
# third party imports
from datetime import datetime
# local imports
from employer.models import Employer , EmployerOrder
from package.models import PurchasedPackage

# can not make job opportunity if they do not have any packages
def can_create_offer(employer , priority) :
    purchased = PurchasedPackage.objects.filter(employer=employer , package__type="offer"  , package__priority=priority,  active=True).order_by('bought_at')
    if purchased.exists() :
        return purchased.first()
    return False



# can not make job opportunity if their package is 0 ( not active) => when the user
def check_package_remaining(purchased_package)   :
    if purchased_package.package.type == 1 :
        return False
    remaining = purchased_package.remaining
    if remaining == 0 or purchased_package.active == False:
        purchased_package.active = False
        purchased_package.deleted_at = datetime.now()
        purchased_package.save()
        return False
    return True


# check the count of the resume sent for the user base on the package they bought and limit the response
def count_of_resume_to_check(employer) :
    # employer packages with type of 1 (resume)
    total = 0
    purchased_packages = PurchasedPackage.objects.filter(employer=employer ,package__type=1)
    for package in purchased_packages.all() :
        total += package.remaining
    return int(total)

def employer_exists(user) :
    try :
        employer = Employer.objects.get(user=user)
    except Employer.DoesNotExist :  
        return False
    return employer

def create_random_number() :
    number = random.randint(300000 , 1000000)
    payment = EmployerOrder.objects.filter(order_id=number)
    if payment.exists() :
        create_random_number()
    return number