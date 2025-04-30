from icecream import ic
from typing_extensions import Iterable

def filter_query(filter_list:Iterable , data) :
    kwargs = {}
    for key , value in data.items() :
        if key in filter_list :
            if value == 'True' :
                value = True
            elif value == 'False':
                value = False
            kwargs.update(
                {key : value}
            )
    return kwargs