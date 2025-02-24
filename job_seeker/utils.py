# django & rest
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK , HTTP_201_CREATED , HTTP_400_BAD_REQUEST , HTTP_404_NOT_FOUND 
# third party imports
from guardian.shortcuts import assign_perm
# local
from job_seeker.models import JobSeeker
from job_seeker.serializers import ResumeSerializer



def assign_base_permissions(user , instance , model) :
    permission = [f'delete_{model}' , f'change_{model}' , f'view_{model}']
    for perm in permission :
        assign_perm(perm , user , instance)
        
        
def job_seeker_exists(user) : 
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