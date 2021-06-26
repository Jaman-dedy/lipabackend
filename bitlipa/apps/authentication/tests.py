import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from bitlipa.resources import error_messages


class UserRegistrationAPIViewTestCase(APITestCase):
    def setUp(self) -> None:
        self.url = reverse('auth-signup')

    def test_user_registration(self):
        user_data = {
            "email": "johnsmith@gmail.com",
            "password": "Password@123",
            "phonenumber": "+9999999999",
            "PIN": "1234"
        }
        response = self.client.post(self.url, json.dumps(user_data), content_type='application/json')
        response_content = json.loads(response.content)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertIn('data', response_content)

    def test_user_registration_email_required(self):
        user_data = {
            "email": "",
            "password": "Password@123",
            "phonenumber": "+9999999999",
            "PIN": "1234"
        }
        response = self.client.post(self.url, json.dumps(user_data), content_type='application/json')
        response_content = json.loads(response.content)
        self.assertIn('message', response_content)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(error_messages.REQUIRED.format('Email is '), response_content.get('message'))

    def test_user_registration_phonenumber_required(self):
        user_data = {
            "email": "johnsmith@gmail.com",
            "password": "Password@123",
            "phonenumber": "",
            "PIN": "1234"
        }
        response = self.client.post(self.url, json.dumps(user_data), content_type='application/json')
        response_content = json.loads(response.content)
        self.assertIn('message', response_content)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(error_messages.REQUIRED.format('Phone number is '), response_content.get('message'))

    def test_user_registration_wrong_phonenumber(self):
        user_data = {
            "email": "johnsmith@gmail.com",
            "password": "Password@123",
            "phonenumber": "+123",
            "PIN": "1234"
        }
        response = self.client.post(self.url, json.dumps(user_data), content_type='application/json')
        response_content = json.loads(response.content)
        self.assertIn('message', response_content)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(error_messages.WRONG_PHONE_NUMBER, response_content.get('message'))


class UserLoginAPIViewTestCase(APITestCase):
    def setUp(self) -> None:
        self.signup_url = reverse('auth-signup')
        self.login_url = reverse('auth-login')

    def test_user_login(self):
        user_data = {
            "email": "johnsmith@gmail.com",
            "password": "Password@123",
            "phonenumber": "+9999999999",
            "PIN": "1234"
        }
        response = self.client.post(self.signup_url, json.dumps(user_data), content_type='application/json')
        user_login = {
            "email": "johnsmith@gmail.com",
            "PIN": "1234"
        }
        response = self.client.post(self.login_url, json.dumps(user_login), content_type='application/json')
        response_content = json.loads(response.content)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn('data', response_content)

    def test_user_login_email_required(self):
        user_data = {
            "email": "",
            "PIN": "1234"
        }
        response = self.client.post(self.login_url, json.dumps(user_data), content_type='application/json')
        response_content = json.loads(response.content)
        self.assertIn('message', response_content)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(error_messages.REQUIRED.format('Email is '), response_content.get('message'))

    def test_user_login_pin_required(self):
        user_data = {
            "email": "johnsmith@gmail.com",
            "PIN": ""
        }
        response = self.client.post(self.login_url, json.dumps(user_data), content_type='application/json')
        response_content = json.loads(response.content)
        self.assertIn('message', response_content)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(error_messages.REQUIRED.format('PIN is '), response_content.get('message'))
