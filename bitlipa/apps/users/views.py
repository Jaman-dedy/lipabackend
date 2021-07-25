from rest_framework import exceptions as drf_exceptions
from rest_framework import viewsets, status
from rest_framework.decorators import action

from .models import User
from .serializers import UserSerializer
from bitlipa.utils.is_valid_uuid import is_valid_uuid
from bitlipa.utils.http_response import http_response
from bitlipa.resources import error_messages
from bitlipa.utils.auth_util import AuthUtil


class UserViewSet(viewsets.ViewSet):
    """
    API endpoint that allows users to be viewed/edited/deleted.
    """

    @action(methods=['put', 'get'], detail=False, url_path='*', url_name='list_update')
    def list_update(self, request):
        AuthUtil.is_auth(request)

        # list users
        if request.method == 'GET':
            queryset = User.objects.all().order_by('-created_at')
            return http_response(status=status.HTTP_200_OK, data=UserSerializer(queryset, many=True).data)

        # update user
        if request.method == 'PUT':
            user = User.objects.update(email=request.decoded_token.get('email'), **request.data)
            return http_response(status=status.HTTP_200_OK, data=UserSerializer(user).data)

    # get one user
    def retrieve(self, request, pk=None):
        AuthUtil.is_auth(request)
        if pk == 'me':
            return http_response(status=status.HTTP_200_OK, data=UserSerializer(request.user).data)
        if not is_valid_uuid(pk):
            raise drf_exceptions.NotFound(error_messages.NOT_FOUND.format('user '))

        user = User.objects.get(id=pk)

        return http_response(status=status.HTTP_200_OK, data=UserSerializer(user).data)

    # update user
    def update(self, request, pk=None):
        AuthUtil.is_auth(request)
        if pk and not is_valid_uuid(pk):
            raise drf_exceptions.NotFound(error_messages.NOT_FOUND.format('user '))

        user = User.objects.update(id=pk, **request.data)

        return http_response(status=status.HTTP_200_OK, data=UserSerializer(user).data)
