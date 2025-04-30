import random
from datetime import timedelta
# django & rest imports
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK , HTTP_201_CREATED , HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
# third party imports
from datetime import datetime
from guardian.shortcuts import assign_perm
from icecream import ic
# local imports
from employer.models import Employer , JobOpportunity , ViewedResume , ViewedAppliedResume , InterviewSchedule
from employer.serializers import (
    EmployerSerializer ,
    JobOpportunitySerializer ,
    ChangeEmployerInterviewScheduleSerializer ,
    ViewedResumeSerializer ,
    AppliedViewedResumeSerializer,
    ChangeApllyStatusSerializer,
    JobOpportunityUpdateSerializer
)
from employer import tasks
from account.models import Message
from package.models import PurchasedPackage
from order.models import Order
from location.utils import get_province , get_city
from job_seeker.models import JobSeeker , Application 
# can not make job opportunity if they do not have any packages
def can_create_offer(employer , priority) :
    ic(priority)
    purchased = PurchasedPackage.objects.filter(employer=employer , package__type="offer"  , package__priority=priority,  active=True).order_by('bought_at')
    ic(PurchasedPackage.objects.filter(employer=employer , package__type="offer" , package__priority=priority))
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
        user.need_complete = False
        user.save()
        return Response(
            data={
                "en_detail" : "Employer registered successfully"
                }, 
            status=HTTP_201_CREATED
        )
    return Response(data={"errors" : serializer.errors} , status=HTTP_400_BAD_REQUEST)


def create_offer(request:object , purchased_packages:object , employer:object , stacks:list) -> Response :
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
                
        offer = serializer.save(employer=employer , city=city , province=province , stack=stacks) 
        purchased_packages.remaining -= 1
        purchased_packages.save()
        message = Message.objects.create(type="expire" , kind="email" , email=user.email)
        warning_eta = offer.expire_at - timedelta(hours=2)
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
    
    serializer = JobOpportunityUpdateSerializer(job_opportunity , data=request.data , partial=True)
    if serializer.is_valid() :
        serializer.save(employer=employer)
        return Response(
                data={
                    "succeeded" : True,
                    "show" : True,
                    "time" : 3000,
                    "en_detail" : "job offer has been updated succesfully",
                    "fa_detail" : "موقعیت شغلی با موفقیت آپدیت شد",
                    "data" : serializer.data ,
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


def view_resume(request:object , employer:object , offer_id:int) -> Response:
    """
    View resume by employer if:
    1) employer has package to see resume
    2) resume was not seen before
    """
    user = request.user
    serializer = ViewedResumeSerializer(data=request.data)
    if serializer.is_valid() :
        data = serializer.validated_data
        resume = data['resume']

        # check if user have purchased packages or not
        purchased = PurchasedPackage.objects.filter(employer=employer , active=True , package__type="resume").order_by('bought_at')
        if not purchased.exists() :
            return Response(data={"detail" : "employer does not have any purchased packages"})
        # check that the employer have this job offer or not
        try :
            offer = JobOpportunity.objects.get(employer=employer, pk=offer_id)
        except JobOpportunity.DoesNotExist :
            return Response(data={"detail" : "offer does not exists"} , status=HTTP_404_NOT_FOUND)
        # avoid duplicate for the resume
        if ViewedResume.objects.filter(employer=employer ,  resume=resume).exists() :
            return Response(data={"detail" : "Resume was seen before"})
        # check that the resume is in the job application or not
        try :
            apply = Application.objects.get(job_opportunity=offer , job_seeker=resume.job_seeker)
        except Application.DoesNotExist :
            return Response(data={"detail" : "apply does not exists"} , status=HTTP_404_NOT_FOUND)

        # change the status of the apply resume to 'seen'
        apply.status = "seen"
        apply.save()
        # save it to the viewed resumes
        serializer.save(employer=employer)
        message = Message.objects.create(type="resume" , kind="email"  , email=user.email)
        tasks.send_resume_status.apply_async(args=[apply.pk , message.pk])
        # minus from the remaining
        purchased_instance = purchased.first()
        new_remaining = purchased_instance.remaining - 1
        purchased_instance.remaining = new_remaining
        purchased_instance.save()

        return Response(data={"success" : True} , status=HTTP_200_OK)
    return Response(data={"success" : False , "errors" : serializer.errors } , status=HTTP_400_BAD_REQUEST)
    
    
def view_applied_resume(request:object , employer:object , apply_id:int) -> Response:
    """View applied resume (change the satus of applied resume to seen)"""
    user = request.user
    serializer = AppliedViewedResumeSerializer(data=request.data)
    if serializer.is_valid() : 
        try :
            # not important to use prefetch related in this situation cause it is just one data 
            apply = Application.objects.prefetch_related('job_seeker').get(pk=apply_id , job_opportunity__employer = employer)
            applied_resume = apply.job_seeker.resume
            job_offer = apply.job_opportunity
            print(applied_resume)
        except Application.DoesNotExist :
            return Response(data={"error" : "job apply does not exists"} , status=HTTP_404_NOT_FOUND)

        purchased = PurchasedPackage.objects.filter(employer=employer , active=True , package__type="resume").order_by('bought_at')
        if not purchased.exists() :
            return Response(
                data={
                    "succeeded" : False,
                    "show" : True,
                    "time" : 3000,
                    "en_detail" : "employer does not have any purchased packages",
                    "fa_detail" : "کاربر پکیج فعالی ندارد"
                }
            )
                
                
        # check that employer viewed this resume for the apply before or not
        viewed_applied_resume = ViewedAppliedResume.objects.filter(job_offer = job_offer, resume = applied_resume)
        if viewed_applied_resume.exists() :
            return Response(data={"error" : "employer viewed this resume before"} , status=HTTP_400_BAD_REQUEST)

            
        serializer.validated_data['job_offer'] = job_offer
        serializer.validated_data['resume'] = applied_resume
        viewed_applied_resume = serializer.save()
        message = Message.objects.create(type="resume" , kind="email"  , email=user.email)
        tasks.send_resume_status.apply_async(args=[apply.pk , message.pk])
        # minus from the remaining
        purchased_instance = purchased.first()
        new_remaining = purchased_instance.remaining - 1
        purchased_instance.remaining = new_remaining
        purchased_instance.save()
        assign_perm("view_viewedappliedresume" , user , viewed_applied_resume)
        return Response(
            data={
                "show" : False,
                "succeeded" : True ,
                "en_detail" : "resume added to viewed resume that are applied to employer",
                "fa_detail" : "رزومه دیده شد"
            } ,
            status=HTTP_200_OK
        )
        
    return Response(data={"errors" : serializer.errors} , status=HTTP_400_BAD_REQUEST)        


def change_applied_resume_status(request:object ,status:str , apply:object , employer:object) -> Response :
    """
    change the status of resume 
    1) reject 
    2) approved
    3) interview
    """
    
    user = request.user
    serializer = ChangeApllyStatusSerializer(apply , data=request.data , partial=True)
    if serializer.is_valid() :
        status = serializer.validated_data['status']
        serializer.save()
        # create schedule for the apply if the status is interview
        if status == "interview" :
            # check that if there is schedule or not 
            schedule = InterviewSchedule.objects.filter(apply=apply) 
            if schedule.exists() :
                return Response(
                    data={
                        "error" : "there is schedule for this apply" ,
                        "fa_error" : "برنامه برای مصاحبه وجود دارد"
                    } , 
                    status=HTTP_400_BAD_REQUEST
                )
            schedule = InterviewSchedule.objects.create(apply=apply) 
            # give permission to the schedule to the user (employer) and the apply job seeker
            assign_perm("view_interviewschedule" , user , schedule)
            assign_perm("change_interviewschedule" , user , schedule)
            assign_perm("view_interviewschedule" , apply.job_seeker.user , schedule)
            assign_perm("change_interviewschedule" ,  apply.job_seeker.user  , schedule)
            # send the status to the job seeker
        message = Message.objects.create(type="resume" , kind="email"  , email=user.email)
        tasks.send_resume_status.apply_async(args=[apply.pk , message.pk])
        return Response(
            data={
                "succeeded" : True , 
                "data" : serializer.data
            } , 
            status=HTTP_200_OK
        )
    return Response(data={"errors" : serializer.errors} , status=HTTP_400_BAD_REQUEST)


    