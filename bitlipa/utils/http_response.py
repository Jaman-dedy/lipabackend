from rest_framework.response import Response
from rest_framework import status


def http_response(status=status.HTTP_200_OK, data=None, message=None) -> Response:
    response = {
        'status': status,
        'message': message,
        'data': data,
    }
    return Response(status=status, data=response)
