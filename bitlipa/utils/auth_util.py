import contextlib
from rest_framework import exceptions as drf_exceptions

from bitlipa.apps.users.models import User
from bitlipa.resources import error_messages
from bitlipa.utils.jwt_util import JWTUtil
from bitlipa.utils.get_object_attr import get_object_attr


class AuthUtil:
    def is_auth(request, is_admin=None):
        token = request.headers.get("Authorization", default="")
        if not token:
            raise drf_exceptions.PermissionDenied(error_messages.AUTHENTICATION_REQUIRED)
        if 'Bearer' not in token:
            raise drf_exceptions.PermissionDenied(error_messages.WRONG_TOKEN)

        decoded_token = JWTUtil.decode(token.replace('Bearer', '').strip())
        request.decoded_token = decoded_token

        with contextlib.suppress(User.DoesNotExist):
            request.user = User.objects.get(email=decoded_token.get('email'))

        if is_admin is True and get_object_attr(request.user, 'is_admin') is not True:
            raise drf_exceptions.PermissionDenied(error_messages.ACCESS_DENIED)

    def get_token(request):
        token = request.headers.get("Authorization", default="").replace('Bearer', '').strip()
        return token
