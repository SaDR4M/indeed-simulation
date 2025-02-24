from functools import wraps
# django & rest 
from rest_framework.response import Response
from job_seeker.utils import job_seeker_exists

def job_seeker_required(view_func) :
    """
    check job seeker existence 
    1) if user is not job seeker it will return Response with the suitable message
    2) if user is job seeker it will return the job seeker obj
    then call the view function
    """
    @wraps(view_func)
    def wrapper(self , request , *args , **kwargs) :
        job_seeker = job_seeker_exists(request.user)
        if isinstance(job_seeker , Response) :
            return job_seeker # if there is no job seeker it will return a response
        request.job_seeker = job_seeker
        return view_func(self , request , *args , **kwargs) # call the main func
    return wrapper