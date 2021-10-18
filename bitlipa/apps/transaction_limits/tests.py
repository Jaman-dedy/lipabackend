import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from bitlipa.apps.users.models import User
from bitlipa.apps.transaction_limits.models import TransactionLimit
from bitlipa.utils.jwt_util import JWTUtil


class TransactionLimitCrudAPIViewTestCase(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.url = reverse('transaction_limits-create_list_transaction_limits')
        self.user = User(email='johnsmith@gmail.com', is_admin=True)
        self.default_transaction_limit = TransactionLimit(currency="KSH", min_amount=0, max_amount=1, country="Kenya", country_code="KE")
        self.user.save()
        self.default_transaction_limit.save()

    def test_transaction_limit_creation(self):
        transaction_limit_data = {
            "currency": "KSH",
            "min_amount": 0,
            "max_amount": 10,
            "country": "Kenya",
            "country_code": "KE",
            "description": "",
        }
        token = JWTUtil.encode({'email': self.user.email})
        headers = {'HTTP_Authorization': f'Bearer {token}'}
        response = self.client.post(self.url, json.dumps(transaction_limit_data), content_type='application/json', **headers)
        response_content = json.loads(response.content)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertIn('data', response_content)

    def test_transaction_limit_creation_max_amount_required(self):
        transaction_limit_data = {
            "currency": "KSH",
            "min_amount": 0,
            "country": "Kenya",
            "country_code": "KE",
            "description": "",
        }
        token = JWTUtil.encode({'email': self.user.email})
        headers = {'HTTP_Authorization': f'Bearer {token}'}
        response = self.client.post(self.url, json.dumps(transaction_limit_data), content_type='application/json', **headers)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_update_transaction_limit(self):
        transaction_limit_data = {
            "currency": "KSH",
            "min_amount": 0,
            "max_amount": 200,
            "country": "Kenya",
            "country_code": "KE",
            "description": "",
        }
        token = JWTUtil.encode({'email': self.user.email})
        headers = {'HTTP_Authorization': f'Bearer {token}'}

        response = self.client.put(f'{self.url}{self.default_transaction_limit.id}/', json.dumps(transaction_limit_data), content_type='application/json', **headers)
        response_content = json.loads(response.content)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn('data', response_content)

    def test_get_transaction_limits(self):
        token = JWTUtil.encode({'email': self.user.email})
        headers = {'HTTP_Authorization': f'Bearer {token}'}
        response = self.client.get(self.url, content_type='application/json', **headers)
        response_content = json.loads(response.content)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn('data', response_content)

    def test_get_one_transaction_limit(self):
        token = JWTUtil.encode({'email': self.user.email})
        headers = {'HTTP_Authorization': f'Bearer {token}'}
        response = self.client.get(f'{self.url}{self.default_transaction_limit.id}/', content_type='application/json', **headers)
        response_content = json.loads(response.content)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn('data', response_content)

    def test_delete_transaction_limit(self):
        token = JWTUtil.encode({'email': self.user.email})
        headers = {'HTTP_Authorization': f'Bearer {token}'}
        response = self.client.delete(f'{self.url}{self.default_transaction_limit.id}/', content_type='application/json', **headers)
        response_content = json.loads(response.content)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn('data', response_content)
