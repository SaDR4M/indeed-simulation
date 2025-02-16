# standard libary imports

# Third party imports
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from unittest.mock import patch

# local imports
from .models import User

# Create your tests here

class SignInTestCase(TestCase) :
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(phone="09036700953" , password="sadra1383")
        self.url = reverse('signin')

    def test_signin_valid_credential(self):
        data = {
            "phone" : "09036700953",
            "password" : "sadra1383"
        }
        response = self.client.post(self.url , data , format='json')
        self.assertEqual(response.status_code , status.HTTP_201_CREATED)
        self.assertIn('access' , response.data['tokens'])
        self.assertIn('refresh' , response.data['tokens'])

    def test_signin_credentials_wrong_password(self):
        data = {
            "phone" : "09036700953",
            "password" : "13832004"
        }
        response = self.client.post(self.url , data , format='json')
        self.assertEqual(response.status_code , status.HTTP_400_BAD_REQUEST)
        self.assertIn('invalid credentials' , response.data['detail'])

    def test_signin_credentials_wrong_phone(self):
        data = {
            "phone" : "09036700943",
            "password" : "sadra1383"
        }
        response = self.client.post(self.url , data , format='json')
        self.assertEqual(response.status_code , status.HTTP_404_NOT_FOUND)



class GetOtpTestCase(TestCase) :
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('get_otp')

    def test_get_otp(self):
        data = {
            "phone" : "09036700953",
        }
        response = self.client.get(self.url , data , format='json')
        self.assertEqual(response.status_code , status.HTTP_200_OK)
        self.assertIn('otp' , response.data)

    # def test_get_otp_wrong_phone(self):
    #     data = {
    #         "phone" : "09036700943",
    #     }
    #     response = self.client.get(self.url , data , format='json')
    #     self.assertEqual(response.status_code , status.HTTP_404_NOT_FOUND)




class VerifyOtpTestCase(TestCase) :
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('verify_otp')

    @patch('account.views.verify_otp')
    def test_verify_otp_correct_otp(self , mock_verify_otp) :
        mock_verify_otp.return_value = True

        data = {
            "phone" : "09036700953",
            "otp" : "123456"
        }
        response = self.client.post(self.url , data , format='json')
        self.assertEqual(response.status_code , status.HTTP_200_OK)
        self.assertIn('user_exist' , response.data)
        self.assertIn('otp_valid' , response.data)
        self.assertIn('tokens' , response.data)
        self.assertIn('access' , response.data['tokens'])
        self.assertIn('refresh' , response.data['tokens'])


    @patch('account.utils.verify_otp')
    def test_verify_otp_wrong_otp(self , mock_verify_otp) :
        mock_verify_otp.return_value = False

        data = {
            "phone" : "09036700953",
            "otp" : "123456"
        }

        response = self.client.post(self.url , data , format='json')
        self.assertEqual(response.status_code , status.HTTP_400_BAD_REQUEST)

    @patch('account.utils.verify_otp')
    def test_verify_otp_otp_missing(self , mock_verify_otp ) :
        mock_verify_otp.return_value = False
        data = {
            "phone" : "09036700953",
        }
        response = self.client.post(self.url , data , format='json')
        self.assertEqual(response.status_code , status.HTTP_400_BAD_REQUEST)


    @patch('account.utils.verify_otp')
    def test_verify_otp_phone_missing(self , mock_verify_otp) :
        mock_verify_otp.return_value = True
        data = {
            "otp" : "123456"
        }
        response = self.client.post(self.url , data , format='json')
        self.assertEqual(response.status_code , status.HTTP_400_BAD_REQUEST)



class UpdateCredentialsTestCase(TestCase) :
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(phone="09036700953" , password="sadra1383")
        self.url = reverse('update_credential')
        login_url = reverse('signin')
        data = {"phone" : "09036700953" , "password" : "sadra1383"}
        login_response = self.client.post(login_url, data , format='json')
        self.token = login_response.data['tokens']['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    def test_update_password(self):
        data = {
            "phone" : "09036700953",
            "password" : "sadra1383",
            "confirm_password" : "sadra1383"
        }
        response = self.client.patch(self.url , data , format='json')
        self.assertEqual(response.status_code , status.HTTP_200_OK)

    def test_update_email(self):
        data = {
            "phone" : "09036700953",
            "email" : "mjanloo83@gmail.com"
        }
        response = self.client.patch(self.url , data , format='json')
        self.assertEqual(response.status_code , status.HTTP_200_OK)

    def test_update_password_not_match(self):
        data = {
            "phone" : "09036700953",
            "password" : "sadra1383",
            "confirm_password" : "sadra1382"
        }
        response = self.client.patch(self.url , data , format='json')
        self.assertEqual(response.status_code , status.HTTP_400_BAD_REQUEST)

    def test_update_user_not_found(self):
        data = {
            "phone" : "09036700943",
        }
        response = self.client.patch(self.url , data , format='json')
        self.assertEqual(response.status_code , status.HTTP_404_NOT_FOUND)

    def test_update_phone_missing(self):
        data = {
            "email" : "test@gmail.com"
        }
        response = self.client.patch(self.url , data , format='json')
        self.assertEqual(response.status_code , status.HTTP_400_BAD_REQUEST)