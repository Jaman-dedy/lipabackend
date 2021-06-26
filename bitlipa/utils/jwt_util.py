import jwt
import datetime
from rest_framework import exceptions as drf_exceptions

from bitlipa import settings
from bitlipa.resources import error_messages


class JWTUtil:
    def encode(payload: dict, expiration_hours: int = 24) -> str:
        try:
            return jwt.encode({
                **payload, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=expiration_hours)
            }, settings.SECRET_KEY, algorithm="HS256")

        except jwt.PyJWTError:
            raise drf_exceptions.PermissionDenied(error_messages.INTERNAL_SERVER_ERROR)

    def decode(encoded_jwt: str) -> dict:
        try:
            return jwt.decode(encoded_jwt, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise drf_exceptions.PermissionDenied(error_messages.TOKEN_EXPIRED)
        except jwt.PyJWTError:
            raise drf_exceptions.PermissionDenied(error_messages.WRONG_TOKEN)
