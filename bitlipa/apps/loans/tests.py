import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from bitlipa.apps.users.models import User
from bitlipa.apps.loans.models import Loan
from bitlipa.utils.jwt_util import JWTUtil


class LoanCrudAPIViewTestCase(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.url = reverse('loans-create_list_loans')
        self.user = User(email='johnsmith@gmail.com', is_admin=True)
        self.default_loan = Loan(name="test loan", type="flat", amount=1)
        self.user.save()
        self.default_loan.save()

    def test_loan_creation(self):
        loan_data = {
            "name": "currency exchange",
            "type": "flat",
            "currency": "",
            "amount": 0.1,
            "description": "exchange loan"
        }
        token = JWTUtil.encode({'email': self.user.email})
        headers = {'HTTP_Authorization': f'Bearer {token}'}
        response = self.client.post(self.url, json.dumps(loan_data), content_type='application/json', **headers)
        response_content = json.loads(response.content)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertIn('data', response_content)

    def test_loan_creation_name_required(self):
        loan_data = {
            "name": "",
            "type": "flat",
            "currency": "",
            "amount": 0.1,
            "description": "exchange loan"
        }
        token = JWTUtil.encode({'email': self.user.email})
        headers = {'HTTP_Authorization': f'Bearer {token}'}
        response = self.client.post(self.url, json.dumps(loan_data), content_type='application/json', **headers)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_loan_creation_type_required(self):
        loan_data = {
            "name": "currency exchange",
            "type": "",
            "currency": "",
            "amount": 0.1,
            "description": "exchange loan"
        }
        token = JWTUtil.encode({'email': self.user.email})
        headers = {'HTTP_Authorization': f'Bearer {token}'}
        response = self.client.post(self.url, json.dumps(loan_data), content_type='application/json', **headers)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_update_loan(self):
        loan_data = {
            "name": "test loan",
            "type": "flat",
            "currency": "",
            "amount": 0.15,
            "description": ""
        }
        token = JWTUtil.encode({'email': self.user.email})
        headers = {'HTTP_Authorization': f'Bearer {token}'}

        response = self.client.put(f'{self.url}{self.default_loan.id}/', json.dumps(loan_data), content_type='application/json', **headers)
        response_content = json.loads(response.content)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn('data', response_content)

    def test_get_loans(self):
        token = JWTUtil.encode({'email': self.user.email})
        headers = {'HTTP_Authorization': f'Bearer {token}'}
        response = self.client.get(self.url, content_type='application/json', **headers)
        response_content = json.loads(response.content)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn('data', response_content)

    def test_get_one_loan(self):
        token = JWTUtil.encode({'email': self.user.email})
        headers = {'HTTP_Authorization': f'Bearer {token}'}
        response = self.client.get(f'{self.url}{self.default_loan.id}/', content_type='application/json', **headers)
        response_content = json.loads(response.content)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn('data', response_content)

    def test_delete_loan(self):
        token = JWTUtil.encode({'email': self.user.email})
        headers = {'HTTP_Authorization': f'Bearer {token}'}
        response = self.client.delete(f'{self.url}{self.default_loan.id}/', content_type='application/json', **headers)
        response_content = json.loads(response.content)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn('data', response_content)
