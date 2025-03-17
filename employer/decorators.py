from functools import wraps
# django & rest 
from rest_framework.response import Response
# local
from employer.utils import employer_exists


def employer_required(view_func) :
    @wraps(view_func)
    def wrapper(self , request , *args , **kwargs) :
        employer = employer_exists(request.user)
        if isinstance(employer , Response) :
            return employer
        request.employer = employer
        return view_func(self , request , *args , **kwargs)
    return wrapper