import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from bitlipa.apps.users.models import User
from bitlipa.apps.fees.models import Fee
from bitlipa.utils.jwt_util import JWTUtil


class FeeCrudAPIViewTestCase(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.url = reverse('fees-create_list_fees')
        self.user = User(email='johnsmith@gmail.com', is_admin=True)
        self.default_fee = Fee(name="test fee", type="flat", amount=1)
        self.user.save()
        self.default_fee.save()

    def test_fee_creation(self):
        fee_data = {
            "name": "currency exchange",
            "type": "flat",
            "currency": "",
            "amount": 0.1,
            "description": "exchange fee"
        }
        token = JWTUtil.encode({'email': self.user.email})
        headers = {'HTTP_Authorization': f'Bearer {token}'}
        response = self.client.post(self.url, json.dumps(fee_data), content_type='application/json', **headers)
        response_content = json.loads(response.content)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertIn('data', response_content)

    def test_fee_creation_name_required(self):
        fee_data = {
            "name": "",
            "type": "flat",
            "currency": "",
            "amount": 0.1,
            "description": "exchange fee"
        }
        token = JWTUtil.encode({'email': self.user.email})
        headers = {'HTTP_Authorization': f'Bearer {token}'}
        response = self.client.post(self.url, json.dumps(fee_data), content_type='application/json', **headers)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_fee_creation_type_required(self):
        fee_data = {
            "name": "currency exchange",
            "type": "",
            "currency": "",
            "amount": 0.1,
            "description": "exchange fee"
        }
        token = JWTUtil.encode({'email': self.user.email})
        headers = {'HTTP_Authorization': f'Bearer {token}'}
        response = self.client.post(self.url, json.dumps(fee_data), content_type='application/json', **headers)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_update_fee(self):
        fee_data = {
            "name": "test fee",
            "type": "flat",
            "currency": "",
            "amount": 0.15,
            "description": ""
        }
        token = JWTUtil.encode({'email': self.user.email})
        headers = {'HTTP_Authorization': f'Bearer {token}'}

        response = self.client.put(f'{self.url}{self.default_fee.id}/', json.dumps(fee_data), content_type='application/json', **headers)
        response_content = json.loads(response.content)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn('data', response_content)

    # def test_get_fees(self):
    #     token = JWTUtil.encode({'email': self.user.email})
    #     headers = {'HTTP_Authorization': f'Bearer {token}'}
    #     response = self.client.get(self.url, content_type='application/json', **headers)
    #     response_content = json.loads(response.content)
    #     self.assertEqual(status.HTTP_200_OK, response.status_code)
    #     self.assertIn('data', response_content)

    # def test_get_one_fee(self):
    #     token = JWTUtil.encode({'email': self.user.email})
    #     headers = {'HTTP_Authorization': f'Bearer {token}'}
    #     response = self.client.get(f'{self.url}{self.default_fee.id}/', content_type='application/json', **headers)
    #     response_content = json.loads(response.content)
    #     self.assertEqual(status.HTTP_200_OK, response.status_code)
    #     self.assertIn('data', response_content)

    # def test_delete_fee(self):
    #     token = JWTUtil.encode({'email': self.user.email})
    #     headers = {'HTTP_Authorization': f'Bearer {token}'}
    #     response = self.client.delete(f'{self.url}{self.default_fee.id}/', content_type='application/json', **headers)
    #     response_content = json.loads(response.content)
    #     self.assertEqual(status.HTTP_200_OK, response.status_code)
    #     self.assertIn('data', response_content)
