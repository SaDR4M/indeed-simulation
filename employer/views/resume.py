import datetime
from dataclasses import dataclass


# third party imports
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK , HTTP_400_BAD_REQUEST , HTTP_403_FORBIDDEN , HTTP_404_NOT_FOUND
from guardian.shortcuts import assign_perm
from rest_framework.pagination import LimitOffsetPagination
# local imports
from employer.serializers import (
                        GetJobOpportunitySerializer,
                        ViewedResumeSerializer,
                        GetViewedResumeSerializer,
                        ChangeApllyStatusSerializer,
                        AppliedViewedResumeSerializer ,
                        GetAppliedViewedResumeSerializer
                          )
                          
from employer.models import JobOpportunity, ViewedResume , InterviewSchedule , ViewedAppliedResume 
from job_seeker.models import Resume , Application
from job_seeker.serializers import ApplicationSerializer, GetResumeSerializer
from employer.utils import  employer_exists
from employer.mixins import  FilterResumeMixin 
from rest_framework.pagination import LimitOffsetPagination
from employer.docs import (
    resume_for_offer_get_doc,
    resume_viewer_get_doc,
    resume_viewer_post_doc,
    all_resume_get_doc,
    applied_resume_viewer_get_doc,
    applied_resume_viewer_post_doc,
    change_apply_status_patch_doc
)
from account.models import Message
from employer import tasks
from package.models import PurchasedPackage




# view the resume that job seekers sent to the employer for specific job opportunity
class ResumesForOffer(APIView) :
    
    @resume_for_offer_get_doc
    def get(self , request) :
        user = request.user
        offer_id = request.data.get('offer_id')
        # check if employer exists
        if not offer_id :
            return Response(data={"detail" : "offer_id must be enter"} , status=HTTP_400_BAD_REQUEST)
        employer = employer_exists(user)
        if not employer :
            return Response(data={"detail" : "Employer does not exists"} , status=HTTP_404_NOT_FOUND)
        # check if the offer is for the employer
        offer = JobOpportunity.objects.filter(employer=employer , pk=offer_id)
        if not offer.exists() :
            return Response(data={"detail" : "Offer not exists"} , status=HTTP_404_NOT_FOUND)
        # get all resumes
        # ordering in the ascending to show the user latest resume first ( without - )
        applies = Application.objects.filter(job_opportunity=offer.first()).order_by('send_at')
     
        # check if any resume were send to for the offer
        if not applies.exists() :
            return Response(data={"detail" : "there is no apply for this offer yet"} , status=HTTP_404_NOT_FOUND)
        serializer = ApplicationSerializer(applies , many=True)
        return Response(data={"data" : serializer.data} ,status=HTTP_200_OK)
    

class AllResumes(APIView , FilterResumeMixin) : 
    
    @all_resume_get_doc
    def get(self , request) :  
        """get all resumes and apply some filtering to them"""
        user = request.user
        employer = employer_exists(user)
        if not employer :
            return Response(data={"detail" : "Employer does not exists"} , status=HTTP_404_NOT_FOUND)

        # EXCLUCDE resumes that employer seen it before
        viewed_resumes = list(ViewedResume.objects.filter(employer=employer).values_list('resume' , flat=True))
        viewed_applied_resumes = list(ViewedAppliedResume.objects.filter(job_offer__employer=employer).values_list('resume' , flat=True))
        # EXCLUCDE resumes that job seekers applied for the employers
        applied_resumes = list(Application.objects.filter(job_opportunity__employer = employer).values_list('job_seeker__resume' , flat=True))
        all_excluded_ids = set(viewed_resumes + viewed_applied_resumes + applied_resumes)
        resumes = Resume.objects.exclude(id__in = all_excluded_ids)
        
        filtered_resume = self.filter_resume('resume' , resumes)
        # return response if there was any problem
        if isinstance(filtered_resume , Response) :
            return filtered_resume
        # paginate the result 
        paginator = LimitOffsetPagination()
        paginator.paginate_queryset(filtered_resume , request)
        
        serializer = GetResumeSerializer(filtered_resume , many=True)
        return Response(data={"data" : serializer.data} , status=HTTP_200_OK)  
    
    


# transfer the resume to the seen resumes and minus from the remaining 
class ResumeViewer(APIView , FilterResumeMixin) :
    
    """get the all viewed resume by employer . it can be fitlered"""
    @resume_viewer_get_doc
    def get(self , request) :
        user = request.user
        employer = employer_exists(user)
        if not employer:
            return Response(data={"error" : "employer does not exists"} , status=HTTP_404_NOT_FOUND)
        
        viewed_resumes = ViewedResume.objects.filter(employer=employer)
        
        # filter viewed resume
        filter_data = self.filter_resume("viewed_resume" , viewed_resumes)
        if isinstance(filter_data , Response) :
            return filter_data
        

            
        # paginate the data
        paginator = LimitOffsetPagination()
        paginator.paginate_queryset(filter_data , request)
        
        data = []
        # show resume in the viewed resumes
        for viewed_resume in filter_data :
            viewed_resume_serializer = GetViewedResumeSerializer(viewed_resume).data
            resume_serializer_serializer = GetResumeSerializer(viewed_resume.resume).data
            viewed_resume_serializer['resume'] = resume_serializer_serializer
            data.append(viewed_resume_serializer)
        return Response(data={'data' : data} , status=HTTP_200_OK) 
     
    
    @resume_viewer_post_doc
    def post(self , request) :
        user = request.user
        employer = employer_exists(user)
        offer_id = request.data.get('offer_id')
        
        if not offer_id :
            return Response(data={"detail" : "must enter the offer id"} , status=HTTP_400_BAD_REQUEST)

        if not employer :
            return Response(data={"detail" : "Employer Does not exists"} , status=HTTP_404_NOT_FOUND)
        serializer = ViewedResumeSerializer(data=request.data)
        # save the resume for the employer the see what resume 
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
    
    
    
    
class AppliedResumeViewer(APIView , FilterResumeMixin) :
    
    @applied_resume_viewer_get_doc
    def get(self , request) :
        """get the all viewed applied resume by employer . it can be fitlered"""
        user = request.user
        employer = employer_exists(user)
        if not employer :
            return Response(data={"error" : "employer does not exists"} , status=HTTP_400_BAD_REQUEST)
        
        
        viewed_applied_resumes = ViewedAppliedResume.objects.filter(job_offer__employer=employer)
        # check permission of user
        for viewed_applied_resume in viewed_applied_resumes :
            if not user.has_perm("view_viewedappliedresume" , viewed_applied_resume) :
                return Response(data={"error" : "user does not have permission to do this action"} , status=HTTP_403_FORBIDDEN)
        # filter the data
        filtered_data = self.filter_resume("viewed_applied_resume" , viewed_applied_resumes)
        if isinstance(filtered_data , Response) :
            return filtered_data
        # paginate the data
        paginator = LimitOffsetPagination()
        paginator.paginate_queryset(filtered_data , request)
        # add resume and job offer to the response
        data = []
        for viewed_resume in filtered_data :
            applied_serializer = GetAppliedViewedResumeSerializer(viewed_resume).data
            # serializer the resume then add it to applied serializer
            resume_serializer = GetResumeSerializer(viewed_resume.resume).data
            applied_serializer['resume'] = resume_serializer
            # serializer the job offer then add it to applied serializer
            offer_serializer = GetJobOpportunitySerializer(viewed_resume.job_offer).data
            applied_serializer['job_offer'] = offer_serializer
            data.append(applied_serializer)
        
        return Response(data={"data" : data} , status=HTTP_200_OK)
  
  
    @applied_resume_viewer_post_doc
    def post(self , request) :
        """add the resume that employer seen in the applied resume to the viewed applied resume"""
        user = request.user
        employer = employer_exists(user)
        if not employer :
            return Response(data={"error" : "employer does not exists" } , status=HTTP_404_NOT_FOUND)

        apply_id = request.data.get('apply_id')
        if not apply_id :
            return Response(data={"error" : "apply_id must be entered"} , status=HTTP_400_BAD_REQUEST)

        
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
                return Response(data={"detail" : "employer does not have any purchased packages"})
                
                
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
            return Response(data={"success" : True , "detail" : "resume added to viewed resume that are applied to employer"} , status=HTTP_200_OK)
        
        return Response(data={"errors" : serializer.errors} , status=HTTP_400_BAD_REQUEST)        



# employer change the status of the applies
class ChangeApplyStatus(APIView) :
    
    @change_apply_status_patch_doc
    def patch(self , request) :
        user = request.user 
        apply_id = request.data.get('apply_id') 
        status = request.data.get('status')
        if not status :
            return Response(data={"detail" : "status must be enetered"} , status=HTTP_400_BAD_REQUEST)
        if not apply_id :
            return Response(data={"detail" : "apply_id must be entered"} , status=HTTP_400_BAD_REQUEST)
        employer = employer_exists(user)
        if not employer :
            return Response(data={"detail" : "employer does not exists"} , status=HTTP_404_NOT_FOUND)
        # check that the offer is for the employer or not 
        
        if not user.has_perm("change_application") :
            return Response(data={"error" : "user does not have permission to do this action"} , status=HTTP_403_FORBIDDEN)
        try :
            apply = Application.objects.get(pk=apply_id , job_opportunity__employer=employer)
        except Application.DoesNotExist :
            return Response(data={"detail" : "job apply does not exists"} , status=HTTP_404_NOT_FOUND)   
        
        # change the status of the apply
        serializer = ChangeApllyStatusSerializer(apply , data=request.data , partial=True)
        if serializer.is_valid() :
            status = serializer.validated_data['status']
            serializer.save()
            # create schedule for the apply if the status is interview
            if status == "interview" :
                # check that if there is schedule or not 
                schedule = InterviewSchedule.objects.filter(apply=apply) 
                if schedule.exists() :
                    return Response(data={"error" : "there is schedule for this apply" , "fa_error" : "برنامه برای مصاحبه وجود دارد"} , status=HTTP_400_BAD_REQUEST)
                schedule = InterviewSchedule.objects.create(apply=apply) 
                # give permission to the schedule to the user (employer) and the apply job seeker
                assign_perm("view_interviewschedule" , user , schedule)
                assign_perm("change_interviewschedule" , user , schedule)
                assign_perm("view_interviewschedule" , apply.job_seeker.user , schedule)
                assign_perm("change_interviewschedule" ,  apply.job_seeker.user  , schedule)
            # send the status to the job seeker
            message = Message.objects.create(type="resume" , kind="email"  , email=user.email)
            tasks.send_resume_status.apply_async(args=[apply.pk , message.pk])
            return Response(data={"success" : True , "data" : serializer.data} , status=HTTP_200_OK)
        return Response(data={"errors" : serializer.errors} , status=HTTP_400_BAD_REQUEST)

        
  
        

  
  
