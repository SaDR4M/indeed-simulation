from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

all_provinces_get_doc = swagger_auto_schema(
    operation_description="list of all provinces",
    operation_summary="list of all provinces",
    responses= {
        200 : openapi.Response(
            description=200,
            examples={
                "application/json" :
                        [
                            {
                                "id": 1,
                                "name": "اسکو",
                                "slug": "اسکو",
                                "province_id": 1
                            },
                            {
                                "id": 2,
                                "name": "اهر",
                                "slug": "اهر",
                                "province_id": 1
                            },
                        ]
                }
        )
    }
)
all_cities_get_doc = swagger_auto_schema(
    operation_description="list of all cities",
    operation_summary="list of all cities",
    responses={
        200 : openapi.Response(
        description="successful",
        examples={
            "application/json" :
                    [
                        {
                            "id": 1,
                            "name": "آذربایجان شرقی",
                            "slug": "آذربایجان-شرقی",
                            "tel_prefix": "041"
                        },
                        {
                            "id": 2,
                            "name": "آذربایجان غربی",
                            "slug": "آذربایجان-غربی",
                            "tel_prefix": "044"
                        },
                    ]
            }
    )
        }
)
province_cities_get_doc = swagger_auto_schema(
    operation_description="list of a province cities",
    operation_summary="list of a province cities",
    manual_parameters=[
        openapi.Parameter(name="province_id" , in_=openapi.IN_QUERY , description="province id" , type=openapi.TYPE_INTEGER ),
    ],
    responses={
        200 : openapi.Response(
        description="successful",
        examples={
            "application/json" :
                    [
                        {
                            "id": 1,
                            "name": "آذربایجان شرقی",
                            "slug": "آذربایجان-شرقی",
                            "tel_prefix": "041"
                        },
                        {
                            "id": 2,
                            "name": "آذربایجان غربی",
                            "slug": "آذربایجان-غربی",
                            "tel_prefix": "044"
                        },
                    ]
            }
        )
    }
)