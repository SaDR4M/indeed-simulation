from django.shortcuts import render
# third party imports
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
# local imports
from .serializers import PaymentSerializer
from employer.models import Employer
# Create your views here.

class CreatePayment(APIView) :
    def post(self , request) :
        user = request.user
        try :
            employer = Employer.objects.get(user=user)
        except Employer.DoesNotExist :
            return Response(data={"detail" : "employer does not exists"} , status=status.HTTP_400_BAD_REQUEST)
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid() : 
            data = serializer.validated_data
            data['employer'] = employer
            serializer.save()
            return Response(data={"detail" : "payment creation was successfull"} , status=status.HTTP_200_OK)
        return Response(data={"detail" : serializer.errors} , status=status.HTTP_400_BAD_REQUEST)