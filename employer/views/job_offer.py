import datetime
# tdjango & rest
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK , HTTP_201_CREATED , HTTP_400_BAD_REQUEST , HTTP_403_FORBIDDEN , HTTP_404_NOT_FOUND
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.pagination import LimitOffsetPagination
# third party 
from guardian.shortcuts import assign_perm
# local 
from employer.serializers import JobOpportunitySerializer , GetJobOpportunitySerializer      
from employer.models import JobOpportunity
from employer.utils import can_create_offer , employer_exists , check_package_remaining
from employer.mixins import FilterJobOpportunityMixin 
from employer import docs 
from account.models import Message
from employer import tasks
from location.utils import get_city , get_province
# Create your views here.
class JobOffer(APIView , FilterJobOpportunityMixin) :
    
    @docs.job_offer_get_doc
    def get(self , request):
        user = request.user
        # check for employer exist
        employer = employer_exists(user)
        if not employer :
            return Response(data={"en_detail" : "employer does not exists"} , status=HTTP_404_NOT_FOUND)
        # check for offers to exist
        job_opportunities = JobOpportunity.objects.filter(employer=employer)
        # if not job_opportunities.exists() :
        #     return Response(data={"detail" : "there is no opportunity for this employer"})
        # if not user.has_perm('view_jobopportunity' , job_opportunities) :
        #     return Response(data={"detail" : "user does not have permissions for this action"} , status=HTTP_403_FORBIDDEN)

        filter_job_offers = self.filter_job_opportunity(job_opportunities)
        if isinstance(filter_job_offers , Response) :
            return filter_job_offers
        
        # paginate the data
        paginator = LimitOffsetPagination()
        paginator.paginate_queryset(filter_job_offers , request)
        
        serializer = GetJobOpportunitySerializer(filter_job_offers , many=True)
        return Response(data={"detail" : serializer.data } , status=HTTP_400_BAD_REQUEST)
    
    
    @docs.job_offer_post_doc
    def post(self , request) :
        user = request.user
        priority = request.data.get('priority')
        
        if not priority :
            return Response(data={"detail" : "enter the priority"})
        
        # check for employer to exist
        employer = employer_exists(user)
        if not employer :
            return Response(data={"en_detail" : "employer does not exists"} , status=HTTP_404_NOT_FOUND)
        # check the employer package purchased and order it base on the date of purchase
        purchased_packages = can_create_offer(employer  , priority)
        # check that user can make offer or not
        if not purchased_packages :
            return Response(
                data = {
                    "succeeded" : False,
                    "show" : True,
                    "time" : 3000,
                    "en_detail" : "there is no purchase package for this user" , 
                    "fa_detail" : "پکیج فعالی برای شما یافت نشد"
                } ,
                status=HTTP_404_NOT_FOUND
            )
        # check the remaining count of request pacakge
        # *implementing this util is wrong cause if the serialzier is be  invalid (for any reason ) the remaining will be minus but the offer will not save*
        if not check_package_remaining(purchased_packages) :
            return Response(
                data={
                    "succeeded" : False,
                    "show" : True,
                    'time' : 3000,
                    "en_detail" : "there is no remaining for this package",
                    "fa_detail" : "به سقف استفاده از ثبت رزومه با پکیج فعلی رسیده اید"
                    } , 
                status=HTTP_404_NOT_FOUND)
        # save the date
        serializer = JobOpportunitySerializer(data=request.data)
        if serializer.is_valid() :
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

    
    
    @docs.job_offer_patch_doc
    def patch(self , request) :
        user = request.user
        offer_id = request.data.get('offer_id')
        if not offer_id :
            return Response(data={"detail" : "offer_id must be entered"} , status=HTTP_400_BAD_REQUEST)
        employer = employer_exists(user)
        if not employer :
            return Response(data={"detail" : "employer does not exists"} , status=HTTP_404_NOT_FOUND)
        
        try :
            job_opportunity = JobOpportunity.objects.get(employer=employer , pk=offer_id)
        except JobOpportunity.DoesNotExist :
            return Response(data={"detail" : "not found"} , status=HTTP_404_NOT_FOUND)
        
        if not user.has_perm('view_jobopportunity' , job_opportunity) :
            return Response(data={"detail" : "user does not have permissions for this action"} , status=HTTP_403_FORBIDDEN)
        serializer = JobOpportunitySerializer(job_opportunity , data=request.data , partial=True)
        if serializer.is_valid() :
            serializer.save(employer=employer)
            return Response(data={"data" : serializer.data , "detail" : "job offer updated succesfully"} , status=HTTP_200_OK)
        return Response(data={"errors" : serializer.errors} , status=HTTP_400_BAD_REQUEST)

    
    @docs.job_offer_delete_doc
    def delete(self , request):
        user = request.user
        offer_id = request.data.get('offer_id')
        if not offer_id :
            return Response(data={"detail" : "enter the offer id"} , status=HTTP_400_BAD_REQUEST)
        employer = employer_exists(user)
        if not employer :
            return Response(data={"detail" : "employer does not exists"} , status=HTTP_404_NOT_FOUND)
        if not user.has_perm("delete_jobopportunity") :
            return Response(data={"detail" : "employer does not have permission to do this action"} , status=HTTP_403_FORBIDDEN)
        # delete from db
        # JobOpportunity.objects.get(pk=offer_id).delete()
        # virtual delete
        offer = JobOpportunity.objects.filter(pk=offer_id)
        if not offer.exists() :
            return Response(data={"detail" : "offewr does not exists" } , status=HTTP_400_BAD_REQUEST)
        offer.update(active=False , expire_at = datetime.datetime.now().strftime('%Y-%m-%d'))
        return Response(data={"detail" : "deleted successfully" } , status=HTTP_200_OK)
    
class AllJobOffers(APIView  , FilterJobOpportunityMixin) :

    @docs.all_offers_get_doc
    def get(self , request):
        job_opportunities = JobOpportunity.objects.all()
        
        filtered_job_offer = self.filter_job_opportunity(job_opportunities)
        if isinstance(filtered_job_offer , Response) :
            return filtered_job_offer
        
        # paginate the data
        paginator = LimitOffsetPagination()
        paginator.paginate_queryset(filtered_job_offer , request)
        
        serializer = GetJobOpportunitySerializer(filtered_job_offer , many=True)
        return Response(data={"detail" : serializer.data } , status=HTTP_200_OK)
    
    