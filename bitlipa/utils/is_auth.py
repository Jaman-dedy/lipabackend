from rest_framework import exceptions as drf_exceptions
from bitlipa.resources import error_messages


def is_auth(request):
    token = request.headers.get("Authorization", default="")
    if not token:
        raise drf_exceptions.PermissionDenied(error_messages.AUTHENTICATION_REQUIRED)
    if 'Bearer' not in token:
        raise drf_exceptions.PermissionDenied(error_messages.WRONG_TOKEN)
