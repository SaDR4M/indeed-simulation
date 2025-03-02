# django & rest
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK , HTTP_201_CREATED , HTTP_400_BAD_REQUEST , HTTP_404_NOT_FOUND 
# third party imports
from guardian.shortcuts import assign_perm
# local
from job_seeker.models import JobSeeker , Application
from job_seeker.serializers import ResumeSerializer
from job_seeker.serializers import ApplicationSerializer , JobSeekerSerializer
from employer.models import JobOpportunity
from location.utils import get_city , get_province
from job_seeker.serializers import  ChangeJobSeekerInterviewScheduleSerializer 




def assign_base_permissions(user , instance , model) :
    """
    Assign base permissions (view , change , delete) for an object to a user
    """
    permission = [f'delete_{model}' , f'change_{model}' , f'view_{model}']
    for perm in permission :
        assign_perm(perm , user , instance)
        
        
def job_seeker_exists(user) : 
    """Check if user is job seeker or not"""
    try :
        job_seeker = JobSeeker.objects.get(user=user)
    except JobSeeker.DoesNotExist :
        return Response(
            data = {
                "en_detail" : "Job seeker does not exists"
            },
            status = HTTP_404_NOT_FOUND
        )
    return job_seeker


def create_resume(request:object , job_seeker:object , user:object) -> Response :
    """Create resume for job seeker"""
    serializer = ResumeSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        data['job_seeker'] = job_seeker
        resume = serializer.save()
        # assign the basic permission to the user
        # its better handle this in signals cause there is security problem if we create the resume and the assign does not work
        assign_base_permissions(user , resume , "resume")
        return Response(data={"detail" : "resume created successfully"}, status=HTTP_201_CREATED)
    return Response(data={"errors" : serializer.errors}, status=HTTP_400_BAD_REQUEST) 


def apply_for_job(request:object , offer_id:int , job_seeker:object ) -> Response :
    """Apply job seeker resume for a specific job opportunity"""
    user = request.user
        
    serializer = ApplicationSerializer(data=request.data)
    if serializer.is_valid() :
        data = serializer.validated_data
        try :
            job_opportunity = JobOpportunity.objects.get(pk=offer_id , status="approved")
        except JobOpportunity.DoesNotExist :
                return Response(data={"error"  : "job opportunity does not exist"})
            
        apply = Application.objects.filter(job_seeker=job_seeker , job_opportunity=job_opportunity)
            
        if apply.exists() : 
            return Response(data={"error" : "job seeker applied for this job before"} , status=HTTP_400_BAD_REQUEST)
            
        data['job_seeker'] = job_seeker
        data['job_opportunity'] = job_opportunity
   
        application = serializer.save()
            # assign the permission to view/delete the offer later
        assign_perm('view_application' , user , application)
        assign_perm('delete_application' , user , application)
        assign_perm('view_application' , job_opportunity.employer.user , application)
        assign_perm('change_application' , job_opportunity.employer.user , application)
        return Response(data={"detail" : "job application was successfull"} , status=HTTP_201_CREATED)

    return Response(data={"errors" : serializer.errors} , status=HTTP_400_BAD_REQUEST)




def register_job_seeker(request) :
    """Register job seeker"""
    
    user = request.user
    serializer = JobSeekerSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        data['user'] = user
        # adding the city and country
        province_id = request.data.get('province')
        province = get_province(province_id=province_id)
        if isinstance(province , Response) :
            return province
            
        city_id = request.data.get('city')
        city = get_city(province_id=province_id , city_id=city_id)
        if isinstance(city , Response) :
            return city
            
        job_seeker = serializer.save(user=user , city=city , province=province)
        # assign base permission
        assign_base_permissions(user, job_seeker, "jobseeker")
        # change user role
        user.role = 2
        user.need_complete = False
        user.save()
        return Response(
            data={
                "succeeded" : True,
                "show" : True,
                "time" : 3000,
                "en_detail" : "Job Seeker registered successfully",
                "fa_detail" : "حساب شما با موفقیت تکمیل شد"
            }, 
            status=HTTP_201_CREATED
        )
    return Response(data={"errors" : serializer.errors}, status=HTTP_400_BAD_REQUEST)



def change_interview_schedule(request:object , interview:object) -> Response :
    """Change interview schedule"""
    serializer = ChangeJobSeekerInterviewScheduleSerializer(interview ,data=request.data , partial=True)
    if serializer.is_valid() :  
        job_seeker_time = serializer.validated_data['job_seeker_time']
        employer_time = interview.employer_time
        if employer_time :
            if employer_time == job_seeker_time :
                serializer.validated_data['status'] = 'approved'
                serializer.validated_data['interview_time'] = employer_time
            if job_seeker_time != employer_time :
                serializer.validated_data['status'] = 'rejected_by_jobseeker'
                    
        serializer.save()
        return Response(data={"success" : True ,"data" : serializer.data ,"interview_time" :  interview.interview_time } , status=HTTP_200_OK)
    return Response(data={"errors" : serializer.errors} , status=HTTP_400_BAD_REQUEST)