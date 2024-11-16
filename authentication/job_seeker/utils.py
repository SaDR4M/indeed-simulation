# third party imports
from guardian.shortcuts import assign_perm

def assign_base_permissions(user , instance , model) :
    permission = [f'delete_{model}' , f'change_{model}' , f'view_{model}']
    for perm in permission :
        assign_perm(perm , user , instance)