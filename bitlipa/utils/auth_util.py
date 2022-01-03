import contextlib
from rest_framework import exceptions as drf_exceptions
from django.core import exceptions as core_exceptions
from datetime import datetime, timezone

from bitlipa.resources import error_messages
from bitlipa.utils.jwt_util import JWTUtil
from bitlipa.utils.get_object_attr import get_object_attr
from bitlipa.apps.users.models import User
from bitlipa.apps.global_configs.models import GlobalConfig


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

        if get_object_attr(request.user, 'is_account_blocked'):
            raise drf_exceptions.PermissionDenied(error_messages.ACCOUNT_LOCKED_DUE_TO_SUSPICIOUS_ACTIVITIES)

        with contextlib.suppress(GlobalConfig.DoesNotExist):
            max_wrong_login_attempts = GlobalConfig.objects.get(name__iexact='max wrong login attempts')
            if get_object_attr(request.user, 'wrong_login_attempts_count') >= max_wrong_login_attempts.data:
                date_diff = datetime.now(timezone.utc) - get_object_attr(request.user, 'last_wrong_login_attempt_date')
                if date_diff.days < 1:
                    raise core_exceptions.PermissionDenied(error_messages.ACCOUNT_LOCKED_DUE_WRONG_LOGIN_ATTEMPTS)

        if is_admin is True and get_object_attr(request.user, 'is_admin') is not True:
            raise drf_exceptions.PermissionDenied(error_messages.ACCESS_DENIED)

    def get_token(request):
        token = request.headers.get("Authorization", default="").replace('Bearer', '').strip()
        return token
