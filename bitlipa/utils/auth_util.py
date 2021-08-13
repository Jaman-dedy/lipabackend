import contextlib
from rest_framework import exceptions as drf_exceptions

from bitlipa.apps.users.models import User
from bitlipa.resources import error_messages
from bitlipa.utils.jwt_util import JWTUtil


class AuthUtil:
    def is_auth(request):
        token = request.headers.get("Authorization", default="")
        if not token:
            raise drf_exceptions.PermissionDenied(error_messages.AUTHENTICATION_REQUIRED)
        if 'Bearer' not in token:
            raise drf_exceptions.PermissionDenied(error_messages.WRONG_TOKEN)

        decoded_token = JWTUtil.decode(token.replace('Bearer', '').strip())
        request.decoded_token = decoded_token

        try:
            request.user = User.objects.get(email=decoded_token.get('email'))
        except Exception:
            contextlib.suppress(Exception)

    def get_token(request):
        token = request.headers.get("Authorization", default="").replace('Bearer', '').strip()
        return token
