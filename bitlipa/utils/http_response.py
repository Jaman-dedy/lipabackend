from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status


def http_response(status=status.HTTP_200_OK, data=None, message=None, error=None, html=None, content_type=None, meta=None) -> Response:
    if html:
        return HttpResponse(html)

    response = {
        'status': status,
        'message': message,
        'data': data,
        'error': error,
        'meta': meta,
    }
    if status is None:
        response.pop('status', None)
    if message is None:
        response.pop('message', None)
    if data is None:
        response.pop('data', None)
    if error is None:
        response.pop('error', None)
    if meta is None:
        response.pop('meta', None)

    return Response(status=status, data=response, content_type=content_type)
