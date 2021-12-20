from django.conf import settings
from rest_framework.renderers import JSONRenderer
from rest_framework import status

from bitlipa.utils.http_response import http_response
from bitlipa.utils.get_http_error_message_and_code import get_http_error_message_and_code
from bitlipa.resources import error_messages
from bitlipa.utils.logger import logger


class HTTPErrorHandler:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def format_response(self, response):
        response.accepted_renderer = JSONRenderer()
        response.accepted_media_type = "application/json"
        response.renderer_context = {}
        return response

    def process_exception(self, request, exception):
        if settings.DEBUG is True:
            logger(exception, 'exception')

        try:
            error = get_http_error_message_and_code(exception)
            return self.format_response(http_response(status=error.get('code'),
                                                      message=error.get('message'),
                                                      error=error.get('error')))
        except Exception:
            return self.format_response(http_response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=error_messages.INTERNAL_SERVER_ERROR
            ))
