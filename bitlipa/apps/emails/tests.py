import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from bitlipa.apps.users.models import User
from bitlipa.apps.emails.models import Email
from bitlipa.utils.jwt_util import JWTUtil


class EmailCrudAPIViewTestCase(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.url = reverse('emails-create_list_emails')
        self.user = User(email='johnsmith@gmail.com', is_admin=True)
        self.user.save()
        self.default_email = Email(recipients=[self.user.email], body="body")
        self.default_email.save()

    def test_email_creation(self):
        email_data = {
            "recipients": ['johnsmith@gmail.com'],
            "body": "hello"
        }
        token = JWTUtil.encode({'email': self.user.email})
        headers = {'HTTP_Authorization': f'Bearer {token}'}
        response = self.client.post(self.url, json.dumps(email_data), content_type='application/json', **headers)
        response_content = json.loads(response.content)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertIn('data', response_content)

    def test_email_creation_body_required(self):
        email_data = {
            "recipients": ['johnsmith@gmail.com'],
            "body": ""
        }
        token = JWTUtil.encode({'email': self.user.email})
        headers = {'HTTP_Authorization': f'Bearer {token}'}
        response = self.client.post(self.url, json.dumps(email_data), content_type='application/json', **headers)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_email_creation_recipients_required(self):
        email_data = {
            "recipients": [],
            "body": "body"
        }
        token = JWTUtil.encode({'email': self.user.email})
        headers = {'HTTP_Authorization': f'Bearer {token}'}
        response = self.client.post(self.url, json.dumps(email_data), content_type='application/json', **headers)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_get_emails(self):
        token = JWTUtil.encode({'email': self.user.email})
        headers = {'HTTP_Authorization': f'Bearer {token}'}
        response = self.client.get(self.url, content_type='application/json', **headers)
        response_content = json.loads(response.content)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn('data', response_content)

    def test_get_one_email(self):
        token = JWTUtil.encode({'email': self.user.email})
        headers = {'HTTP_Authorization': f'Bearer {token}'}
        response = self.client.get(f'{self.url}{self.default_email.id}/', content_type='application/json', **headers)
        response_content = json.loads(response.content)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn('data', response_content)

    def test_delete_email(self):
        token = JWTUtil.encode({'email': self.user.email})
        headers = {'HTTP_Authorization': f'Bearer {token}'}
        response = self.client.delete(f'{self.url}{self.default_email.id}/', content_type='application/json', **headers)
        response_content = json.loads(response.content)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn('data', response_content)
