from rest_framework.response import Response
from icecream import ic
### some error handling function , used for existace and validation for serializer error 

def validation_error(serialized):
    print(serialized.errors)
    # en_detail = ''
    # for er in serialized.errors:
    #     en_detail +=er
    return Response(
        {
            'succeeded': False,
            'en_detail': 'Serializer Error !! : {}'.format(serialized.errors) ,
            'fa_detail': 'خطای اعتبار سنجی در سریالایزر  داریم {}'.format(serialized.errors),
            'show': True,
            'error_type': 'validation_error'
        },
        status=400
    )


def existence_error(object_name,object_name_fa=''):
    return Response(
        {
            'succeeded': False,
            'en_detail': '{} object does not exist!'.format(object_name),
            'fa_detail': '{} Object  مورد نظر وجود ندارد. '.format(object_name_fa),
            "show": False,   # =====> because in user_info we dont need to show
            'error_type': 'existence_error'
        },
        status=404
    )

def existence_error_show(object_name,object_name_fa=''):
    return Response(
        {
            'succeeded': False,
            'en_detail': '{} does not exist!'.format(object_name),
            'fa_detail': '{} مورد نظر وجود ندارد. '.format(object_name_fa),
            "show": True,   # =====> because in user_info we dont need to show
            'error_type': 'existence_error'
        },
        status=404
    )