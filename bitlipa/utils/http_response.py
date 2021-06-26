from rest_framework.response import Response
from rest_framework import status


def http_response(status=status.HTTP_200_OK, data=None, message=None) -> Response:
    response = {
        'status': status,
        'message': message,
        'data': data,
    }
    if status is None:
        response.pop('status', None)
    if message is None:
        response.pop('message', None)
    if data is None:
        response.pop('data', None)

    return Response(status=status, data=response)
