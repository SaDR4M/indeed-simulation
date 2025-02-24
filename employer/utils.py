import random
# django & rest imports
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK , HTTP_201_CREATED , HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
# third party imports
from datetime import datetime
from guardian.shortcuts import assign_perm
# local imports
from employer.models import Employer
from employer.serializers import EmployerSerializer , JobOpportunitySerializer , ChangeEmployerInterviewScheduleSerializer
from employer import tasks
from account.models import Message
from package.models import PurchasedPackage
from order.models import Order
from location.utils import get_province , get_city

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

def employer_exists(user:object) :
    try :
        employer = Employer.objects.get(user=user)
    except Employer.DoesNotExist :  
        return Response(
            data = {
                "en_detail" : "Employer does not exists"
            },
            status=HTTP_404_NOT_FOUND
        )
    return employer

def create_random_number() :
    number = random.randint(300000 , 1000000)
    payment = Order.objects.filter(order_id=number)
    if payment.exists() :
        create_random_number()
    return number


def create_employer(request:object) -> Response:
    """Create employer"""
    
    serializer = EmployerSerializer(data=request.data)
    if serializer.is_valid() :
        user = request.user
        # TODO fix this
        province_id = request.data.get('province')
        city_id = request.data.get('city')
        # get province data
        province = get_province(
            province_id=province_id
        )
        if isinstance(province , Response) :
            return province
        # get city 
        city = get_city(
            province_id=province_id ,
            city_id=city_id
        )
        if isinstance(city , Response) :
            return city
        # adding the user to the validated data
        employer = serializer.save(
            user=user ,
            city=city,
            province=province
        )
        # assign the permission to the user
        assign_perm('view_employer' , user , employer)
        assign_perm('delete_employer' , user , employer)
        # change user role
        user.role = 1
        user.save()
        return Response(
            data={
                "en_detail" : "Employer registered successfully"
                }, 
            status=HTTP_201_CREATED
        )
    return Response(data={"errors" : serializer.errors} , status=HTTP_400_BAD_REQUEST)


def create_offer(request:object , purchased_packages:object , employer:object) -> Response :
    """Create job opportunity"""
    
    serializer = JobOpportunitySerializer(data=request.data)
    if serializer.is_valid() :
        user = request.user
        # adding city and country
        # TODO fix this
        province_id = request.data.get('province')
        province = get_province(province_id=province_id)
        if isinstance(province , Response) :
            return province
                
        city_id = request.data.get('city')
        city = get_city(province_id=province_id , city_id=city_id)
        if isinstance(city , Response) :
            return city
                
        offer = serializer.save(employer=employer , city=city , province=province)
        purchased_packages.remaining -= 1
        purchased_packages.save()
        message = Message.objects.create(type="expire" , kind="email" , email=user.email)
        warning_eta = offer.expire_at - datetime.timedelta(hours=2)
        tasks.expire_job_offer_warning.apply_async(args=[offer.pk , message.pk] , eta=warning_eta)
        tasks.expire_job_offer.apply_async(args=[offer.pk  ,message.pk] , eta=offer.expire_at)
        # offer.remaining -= 1
        # offer.save()
        # assign permission to the user for its own object
        assign_perm("view_jobopportunity" , user , offer)
        assign_perm("change_jobopportunity" , user , offer)
        assign_perm("delete_jobopportunity" , user , offer)
        return Response(data={"detail" : "Job Opportunity created successfully"} , status=HTTP_201_CREATED)
    return Response(data={"errors" : serializer.errors} , status=HTTP_200_OK)


def update_offer(request:object , job_opportunity:object , employer:object) -> Response :
    """Update job opportunity data"""
    
    serializer = JobOpportunitySerializer(job_opportunity , data=request.data , partial=True)
    if serializer.is_valid() :
        serializer.save(employer=employer)
        return Response(
                data={
                    "data" : serializer.data ,
                    "detail" : "job offer updated succesfully"
                }, 
                status=HTTP_200_OK
            )
    return Response(data={"errors" : serializer.errors} , status=HTTP_400_BAD_REQUEST)

def change_interview_schedule(request:object , interview:object) -> Response :
    """Change interview schedule by Employer"""
    
    serializer = ChangeEmployerInterviewScheduleSerializer(interview ,data=request.data , partial=True)
    if serializer.is_valid() :  
        job_seeker_time = interview.job_seeker_time
        employer_time = serializer.validated_data['employer_time']
        if job_seeker_time :
            if job_seeker_time == employer_time :
                serializer.validated_data['status'] = 'approved'
                serializer.validated_data['interview_time'] = job_seeker_time
            if job_seeker_time != employer_time :
                # interview.job_seeker_time = None
                serializer.validated_data['status'] = 'rejected_by_employer'
        serializer.save()
                
        return Response(data={"success" : True ,"data" : serializer.data ,"interview_time" :  interview.interview_time } , status=HTTP_200_OK)
    return Response(data={"errors" : serializer.errors} , status=HTTP_400_BAD_REQUEST)