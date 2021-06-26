from rest_framework.views import exception_handler

from bitlipa.utils.http_response import http_response
from bitlipa.utils.get_http_error_message_and_code import get_http_error_message_and_code


def http_error_handler(exception, context):
    response = exception_handler(exception, context)
    error = get_http_error_message_and_code(exception)

    if response is not None:
        return http_response(status=error.get('code'), message=error.get('message'))

    return response
