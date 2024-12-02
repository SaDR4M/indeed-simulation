# third party imports
from guardian.shortcuts import assign_perm
# local
from job_seeker.models import JobSeeker
def assign_base_permissions(user , instance , model) :
    permission = [f'delete_{model}' , f'change_{model}' , f'view_{model}']
    for perm in permission :
        assign_perm(perm , user , instance)
        
        
def job_seeker_exists(user) : 
    try :
        job_seeker = JobSeeker.objects.get(user=user)
    except JobSeeker.DoesNotExist :
        return False
    return job_seeker


def can_publish(test) :
    if test.count() == test.count :
        return True
    return False