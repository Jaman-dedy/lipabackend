import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from bitlipa.apps.users.models import User
from bitlipa.apps.crypto_wallets.models import CryptoWallet
from bitlipa.utils.jwt_util import JWTUtil


class CryptoWalletCrudAPIViewTestCase(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.url = reverse('crypto_wallet-create_list_update_wallets')
        self.default_wallet = CryptoWallet(name="sport", address="JAMAN-USD-01", currency="USD")
        user = User(email='johnsmith@gmail.com')
        user.save()
        self.default_wallet.save()

    def test_wallet_creation(self):
        wallet_data = {
            "name": "Business",
            "address": "USD-01-JAMAN",
            "currency": "USD",
        }
        token = JWTUtil.encode({'email': 'johnsmith@gmail.com'})
        headers = {'HTTP_Authorization': f'Bearer {token}'}
        response = self.client.post(self.url, json.dumps(wallet_data), content_type='application/json', **headers)
        response_content = json.loads(response.content)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertIn('data', response_content)

    def test_wallet_creation_name_required(self):
        wallet_data = {
            "name": "",
            "address": "USD-01-JAMAN",
            "currency": "USD",
        }
        token = JWTUtil.encode({'email': 'johnsmith@gmail.com'})
        headers = {'HTTP_Authorization': f'Bearer {token}'}
        response = self.client.post(self.url, json.dumps(wallet_data), content_type='application/json', **headers)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_wallet_creation_currency_required(self):
        wallet_data = {
            "name": "sport",
            "address": "USD-01-JAMAN",
            "currency": "",
        }
        token = JWTUtil.encode({'email': 'johnsmith@gmail.com'})
        headers = {'HTTP_Authorization': f'Bearer {token}'}
        response = self.client.post(self.url, json.dumps(wallet_data), content_type='application/json', **headers)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_update_wallet(self):

        wallet_data = {
            "name": "Business",
            "address": "USD-01-JAMAN",
            "currency": "USD",
        }
        token = JWTUtil.encode({'email': 'johnsmith@gmail.com'})
        headers = {'HTTP_Authorization': f'Bearer {token}'}

        response = self.client.put(f'{self.url}{self.default_wallet.id}/', json.dumps(wallet_data), content_type='application/json', **headers)
        response_content = json.loads(response.content)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn('data', response_content)

    def test_get_wallets(self):
        token = JWTUtil.encode({'email': 'johnsmith@gmail.com'})
        headers = {'HTTP_Authorization': f'Bearer {token}'}
        response = self.client.get(self.url, content_type='application/json', **headers)
        response_content = json.loads(response.content)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn('data', response_content)

    def test_get_one_wallet(self):
        token = JWTUtil.encode({'email': 'johnsmith@gmail.com'})
        headers = {'HTTP_Authorization': f'Bearer {token}'}
        response = self.client.get(f'{self.url}{self.default_wallet.id}/', content_type='application/json', **headers)
        response_content = json.loads(response.content)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn('data', response_content)

    def test_delete_wallet(self):
        token = JWTUtil.encode({'email': 'johnsmith@gmail.com'})
        headers = {'HTTP_Authorization': f'Bearer {token}'}
        response = self.client.delete(f'{self.url}{self.default_wallet.id}/', content_type='application/json', **headers)
        response_content = json.loads(response.content)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn('data', response_content)
