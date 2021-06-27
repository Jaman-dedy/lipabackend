import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from bitlipa.resources import error_messages
from bitlipa.apps.users.models import User
from bitlipa.utils.jwt_util import JWTUtil


class ListUpdateUserAPIViewTestCase(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.url = reverse('users-list_update')
        user = User(email='johnsmith@gmail.com')
        user.save()

    def test_user_update(self):
        user_data = {
            "email": "johnsmith@gmail.com",
            "password": "Password@123",
            "phonenumber": "+9999999999",
            "PIN": "1234"
        }
        token = JWTUtil.encode({'email': 'johnsmith@gmail.com'})
        headers = {'HTTP_Authorization': f'Bearer {token}'}
        response = self.client.put(self.url, json=json.dumps(user_data), content_type='application/json', **headers)
        response_content = json.loads(response.content)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn('data', response_content)

    def test_user_update_not_found(self):
        user_data = {
            "email": "aaa@gmail.com",
            "password": "Password@123",
            "phonenumber": "+9999999999",
            "PIN": "1234"
        }
        token = JWTUtil.encode({'email': 'aaa@gmail.com'})
        headers = {'HTTP_Authorization': f'Bearer {token}'}
        response = self.client.put(self.url, json=json.dumps(user_data), content_type='application/json', **headers)
        response_content = json.loads(response.content)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual(error_messages.NOT_FOUND.format('User '), response_content.get('message'))
