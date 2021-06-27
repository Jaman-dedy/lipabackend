import json
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from bitlipa.apps.users.models import User
from bitlipa.utils.jwt_util import JWTUtil
from bitlipa.resources import error_messages
from bitlipa.utils.test_util import TestUtil


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
        TestUtil.create_user()

        user_login = {
            "email": "johnsmith@example.com",
            "PIN": "1234",
            "device_id": "*#*#8255#*#*",
        }
        response = self.client.post(self.login_url, json.dumps(user_login), content_type='application/json')
        response_content = json.loads(response.content)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn('data', response_content)

    def test_user_login_email_required(self):
        user_data = {
            "email": "",
            "PIN": "1234",
            "device_id": "#*#8255#*#*",
        }
        response = self.client.post(self.login_url, json.dumps(user_data), content_type='application/json')
        response_content = json.loads(response.content)
        self.assertIn('message', response_content)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(error_messages.REQUIRED.format('Email is '), response_content.get('message'))

    def test_user_login_pin_required(self):
        user_data = {
            "email": "johnsmith@gmail.com",
            "PIN": "",
            "device_id": "#*#8255#*#*",
        }
        response = self.client.post(self.login_url, json.dumps(user_data), content_type='application/json')
        response_content = json.loads(response.content)
        self.assertIn('message', response_content)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(error_messages.REQUIRED.format('PIN is '), response_content.get('message'))

    def test_user_login_pin_device_id_required(self):
        TestUtil.create_user()
        user_data = {
            "email": "johnsmith@example.com",
            "PIN": "1234",
            "device_id": "",
        }
        response = self.client.post(self.login_url, json.dumps(user_data), content_type='application/json')
        response_content = json.loads(response.content)
        self.assertIn('message', response_content)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(error_messages.REQUIRED.format('Device id is '), response_content.get('message'))


class UserVerifyEmailAPIViewTestCase(APITestCase):

    def test_verify_email(self):
        token = JWTUtil.encode({'email': 'johnsmith2@example.com', "from_email": True})
        url = reverse('auth-verify_email', args=[token])
        response = self.client.get(url)

        response_content = json.loads(response.content)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn('data', response_content)
        self.assertEqual(True, response_content.get('data').get('is_email_verified'))

    def test_verify_wrong_token(self):
        User(email="johnsmith2@example.com",
             password="Password@123",
             phonenumber="+9999999999",
             pin=make_password("1234"),
             is_email_verified=False,
             is_phone_verified=False,
             ).save()

        token = JWTUtil.encode({'email': 'johnsmith2@example.com', "from_email": False})
        url = reverse('auth-verify_email', args=[token])
        response = self.client.get(url)

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        response_content = json.loads(response.content)
        self.assertEqual(error_messages.WRONG_TOKEN, response_content.get('message'))

    def test_verify_existing_email(self):
        User(email="johnsmith2@example.com",
             password="Password@123",
             phonenumber="+9999999999",
             pin=make_password("1234"),
             is_email_verified=False,
             is_phone_verified=False,
             ).save()

        token = JWTUtil.encode({'email': 'johnsmith2@example.com', "from_email": True})
        url = reverse('auth-verify_email', args=[token])
        response = self.client.get(url)

        self.assertEqual(status.HTTP_409_CONFLICT, response.status_code)
        response_content = json.loads(response.content)
        self.assertEqual(error_messages.CONFLICT.format('johnsmith2@example.com '), response_content.get('message'))


class UserVerifySMSAPIViewTestCase(APITestCase):
    def setUp(self) -> None:
        self.url = reverse('auth-verify_phonenumber')

    def test_verify_sms(self):

        User(email="johnsmith@example.com",
             password="Password@123",
             phonenumber="+9999999999",
             pin=make_password("1234"),
             is_email_verified=False,
             is_phone_verified=False,
             otp="123456"
             ).save()

        token = JWTUtil.encode({'email': 'johnsmith@example.com'})

        user_data = {
            "phonenumber": "+9999999999",
            "OTP": "123456"
        }

        token = JWTUtil.encode({'email': 'johnsmith@example.com'})
        headers = {'HTTP_Authorization': f'Bearer {token}'}
        response = self.client.put(self.url, data=json.dumps(user_data), content_type='application/json', **headers)
        response_content = json.loads(response.content)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn('data', response_content)
        self.assertEqual(True, response_content.get('data').get('is_phone_verified'))

    def test_verify_sms_wrong_token(self):
        User(email="johnsmith@example.com",
             password="Password@123",
             phonenumber="+9999999999",
             pin=make_password("1234"),
             is_email_verified=False,
             is_phone_verified=False,
             otp="123456"
             ).save()

        token = JWTUtil.encode({'email': 'johnsmith@example.com'})

        user_data = {
            "phonenumber": "+9999999999",
            "OTP": "123457"
        }

        token = JWTUtil.encode({'email': 'johnsmith@example.com'})
        headers = {'HTTP_Authorization': f'Bearer {token}'}
        response = self.client.put(self.url, data=json.dumps(user_data), content_type='application/json', **headers)
        response_content = json.loads(response.content)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(error_messages.WRONG_OTP, response_content.get('message'))
