import time
from django.test import TestCase
from django.core import exceptions as core_exceptions
from rest_framework import exceptions as drf_exceptions

from bitlipa.resources import error_messages
from ..jwt_util import JWTUtil


class JWTUtilTestCase(TestCase):
    def setUp(self) -> None:
        self.jwt_payload = {'key': 'value'}

    def test_create_token(self):
        token = JWTUtil.encode({'key': 'value'})
        self.assertEqual(True, isinstance(token, str))

    def test_create_token_wrong_payload(self):
        try:
            JWTUtil.encode('----')
        except Exception as e:
            self.assertEqual(True, isinstance(e, core_exceptions.ValidationError))

    def test_decode_token(self):
        token = JWTUtil.encode(self.jwt_payload)
        decoded_token = JWTUtil.decode(token)
        self.assertIn('key', decoded_token)
        self.assertEqual(self.jwt_payload.get('key'), decoded_token.get('key'))

    def test_decode_token_wrong_token(self):
        try:
            JWTUtil.decode('fake token')
        except Exception as e:
            self.assertEqual(str(e), error_messages.WRONG_TOKEN)
            self.assertEqual(True, isinstance(e, drf_exceptions.PermissionDenied))

    def test_decode_token_expired_token(self):
        try:
            token = JWTUtil.encode(self.jwt_payload, expiration_hours=1 / 3600)
            time.sleep(2)  # sleep for 2 seconds
            JWTUtil.decode(token)
        except Exception as e:
            self.assertEqual(str(e), error_messages.TOKEN_EXPIRED)
            self.assertEqual(True, isinstance(e, drf_exceptions.PermissionDenied))
