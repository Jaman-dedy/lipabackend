import jwt
import datetime
from django.conf import settings
from rest_framework import exceptions as drf_exceptions
from django.core import exceptions as core_exceptions

from bitlipa.resources import error_messages


class JWTUtil:
    def encode(payload: dict, expiration_hours: int = 24) -> str:
        try:
            token = jwt.encode({
                **payload, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=expiration_hours)
            }, settings.SECRET_KEY, algorithm="HS256")
            return str(token, 'utf-8')

        except (jwt.PyJWTError, TypeError):
            raise core_exceptions.ValidationError(error_messages.INTERNAL_SERVER_ERROR)

    def decode(encoded_jwt: str) -> dict:
        try:
            return jwt.decode(encoded_jwt, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise drf_exceptions.PermissionDenied(error_messages.TOKEN_EXPIRED)
        except jwt.PyJWTError:
            raise drf_exceptions.PermissionDenied(error_messages.WRONG_TOKEN)
