import datetime
# tdjango & rest
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK , HTTP_201_CREATED , HTTP_400_BAD_REQUEST , HTTP_403_FORBIDDEN , HTTP_404_NOT_FOUND
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.pagination import LimitOffsetPagination
# third party 
from guardian.shortcuts import assign_perm
from icecream import ic
# local 
from employer.serializers import JobOpportunitySerializer , GetJobOpportunitySerializer      
from employer.models import JobOpportunity
from employer.utils import can_create_offer , create_offer , check_package_remaining , update_offer
from employer.decorators import employer_required
from employer.mixins import FilterJobOpportunityMixin 
from employer import docs 


# Create your views here.
class JobOffer(APIView , FilterJobOpportunityMixin) :
    
    def get(self , request) :
        """Get job offer data"""
        job_offer_id = request.query_params.get("job_offer")
        if not job_offer_id :
            return Response(
                data = {
                    "succeeded" : False,
                    "show" : False,
                    "en_detail" : "job offer must be entered",
                },
                status = HTTP_400_BAD_REQUEST
            )
        try :
            job_offer = JobOpportunity.objects.filter(id=job_offer_id)
        except JobOpportunity.DoesNotExist :
            return Response(
                data = {
                    "succeeded" : False,
                    "show" : True,
                    "time" : 3000,
                    "en_detail" : "job offer does not exists",
                    "fa_detail" : "فرصت شغلی مد نظر یافت نشد"
                },
                status = HTTP_400_BAD_REQUEST
            )
        serializer = GetJobOpportunitySerializer(job_offer.first())
        return Response(
            data = {
                "succeeded" : True,
                "show" : False,
                "data" : serializer.data 
            }
        )
    
    
    
    @docs.job_offer_post_doc
    @employer_required
    def post(self , request) :
        """Create job offer"""
        
        priority = request.data.get('priority')
        
        if not priority :
            return Response(data={"en_detail" : "enter the priority"})
        
        # check for employer to exist
        employer = request.employer
        print(priority)
        print(request.data)
        # TODO purhcased packages
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
        # FIXME *implementing this util is wrong cause if the serialzier is be  invalid (for any reason ) the remaining will be minus but the offer will not save*
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
        # create the offer
        stacks = request.data.get('stack').split(",")
        response = create_offer(request , purchased_packages , employer , stacks)
        return response

    
    
    @docs.job_offer_patch_doc
    @employer_required
    def patch(self , request) :
        """Update job offer"""
        
        user = request.user
        offer_id = request.data.get('offer_id')
        # check if there is a offer or not
        if not offer_id :
            return Response(
                data={
                    "succeeded" : False,
                    "en_detail" : "offer_id must be entered"
                } , 
                status=HTTP_400_BAD_REQUEST
            )
        employer = request.employer
        # get the job opportunity
        try :
            job_opportunity = JobOpportunity.objects.get(
                employer=employer ,
                pk=offer_id
            )
        except JobOpportunity.DoesNotExist :
            return Response(
                data={
                    "succeeded" : False,
                    "show" : True,
                    "time" : 3000,
                    "en_detail" : "offer was not found",
                    "fa_detail" : "فرصت شغلی پیدا نشد"
                } ,
                status=HTTP_404_NOT_FOUND
            )
        # check user permission
        if not user.has_perm('view_jobopportunity' , job_opportunity) :
            return Response(
                data={
                    "succeeded" : False,
                    "show" : True,
                    "time" : 3000,
                    "en_detail" : "user does not have permissions for this action",
                    "fa_detail" : "کاربر مجاز نیست"
                } , 
                status=HTTP_403_FORBIDDEN
            )
        # get stack if exists
        stacks = request.data.get('stacks')
        if stacks :
            stacks_list = stacks.split(",")
            request.data['stacks'] = stacks_list
        response = update_offer(request)
        return response
    
    @docs.job_offer_delete_doc
    @employer_required
    def delete(self , request):
        """Delete job offer"""
        
        user = request.user
        offer_id = request.data.get('offer_id')
        # check if there is a offer or not
        if not offer_id :
            return Response(data={"en_detail" : "enter the offer id"} , status=HTTP_400_BAD_REQUEST)
        # get the offer
        offer = JobOpportunity.objects.filter(employer__user = user , pk=offer_id)
        if not offer.exists() :
            return Response(
                data={
                    "succeeded" : False,
                    "show" : True,
                    "time" : 3000,
                    "en_detail" : "offer does not exists",
                    "fa_detail" : "فرصت شغلی وجود ندارد"
                }
                , 
                status=HTTP_400_BAD_REQUEST
            )
        # check user permission
        # if not user.has_perm("delete_jobopportunity"  , offer.first()) :
        #     return Response(
        #         data={
        #             "succeeded" : False,
        #             "show" : True,
        #             "time" : 3000,
        #             "en_detail" : "employer does not have permission to do this action",
        #             "fa_detail" : "کاربر مجاز نیست"
        #             } , 
        #         status=HTTP_403_FORBIDDEN
        #         )


        # update the offer
        offer.update(deleted=True , expire_at = datetime.datetime.now().strftime('%Y-%m-%d'))
        return Response(
            data={
                "succeeded" : True,
                "time" : 3000,
                "en_detail" : "job offer has beendeleted successfully" ,
                "fa_detail" : "موقعیت شغلی با موفقیت حذف شد"
            } , 
            status=HTTP_200_OK
            )
    
    
    
class JobOfferList(APIView , FilterJobOpportunityMixin) :
    @docs.job_offer_get_doc
    @employer_required
    def get(self , request):
        # check for employer exist
        employer = request.employer
        # check for offers to exist
        job_opportunities = JobOpportunity.objects.filter(employer=employer , deleted=False)
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
        return Response(data={"detail" : serializer.data } , status=HTTP_200_OK)