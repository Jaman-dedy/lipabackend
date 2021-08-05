
import contextlib
from rest_framework import status
from django.http.response import Http404
from django.core import exceptions as core_exceptions
from django.core.paginator import EmptyPage
from rest_framework import exceptions as drf_exceptions
from django.db.utils import IntegrityError

from bitlipa.resources import error_messages
from bitlipa.utils.get_object_attr import get_object_attr
from bitlipa.utils.split_camel_case_words import split_camel_case_words


def get_http_error_message_and_code(exc):
    (error, error_message) = (None, str(get_object_attr(exc, "message", exc)))
    try:
        (error, error_message) = (eval(error_message), error_messages.BAD_REQUEST)
    except Exception:
        contextlib.suppress(Exception)

    if isinstance(exc, (core_exceptions.BadRequest, core_exceptions.ValidationError, drf_exceptions.ValidationError)):
        return {"code": status.HTTP_400_BAD_REQUEST, "message": error_message, "error": error}

    if isinstance(exc, (core_exceptions.PermissionDenied, drf_exceptions.PermissionDenied)):
        return {"code": status.HTTP_401_UNAUTHORIZED, "message": error_message, "error": error}

    if isinstance(exc, (core_exceptions.ObjectDoesNotExist, EmptyPage, drf_exceptions.NotFound, Http404)):
        return {
            "code": status.HTTP_404_NOT_FOUND,
            "message": split_camel_case_words(
                error_message.replace('matching query does not exist.', error_messages.NOT_FOUND.format(''))),
            "error": error
        }
    if isinstance(exc, IntegrityError):
        duplicated_value = error_message[error_message.index(')=(') + 3:error_message.rindex(') already')]\
            if ')=(' in error_message and ') already' in error_message else error_message

        return {
            "code": status.HTTP_409_CONFLICT,
            "message": error_messages.CONFLICT.format(f'{duplicated_value} '),
            "error": error
        }

    return {
        "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "message": error_messages.INTERNAL_SERVER_ERROR,
        "error": error_message
    }
