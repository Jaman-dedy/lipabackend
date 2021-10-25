from rest_framework import viewsets, status
from rest_framework.decorators import action

from .models import Role
from .serializers import RoleSerializer
from bitlipa.utils.is_valid_uuid import is_valid_uuid
from bitlipa.utils.http_response import http_response
from bitlipa.resources import error_messages
from bitlipa.utils.auth_util import AuthUtil


class RoleViewSet(viewsets.ViewSet):
    """
    API endpoint that allows role to be viewed/edited/deleted.
    """
    @action(methods=['post', 'get'], detail=False, url_path='*', url_name='create_list_update_roles')
    def create_list_role(self, request):
        # list roles
        if request.method == 'GET':
            return self.list_roles(request)

        # create role
        if request.method == 'POST':
            return self.create_role(request)

    def create_role(self, request):
        AuthUtil.is_auth(request, is_admin=True)

        serializer = RoleSerializer(Role.objects.create_role(**request.data))

        return http_response(status=status.HTTP_201_CREATED, data=serializer.data)

    def list_roles(self, request):
        AuthUtil.is_auth(request, is_admin=True)

        role = Role.objects.all().order_by('-created_at')
        serializer = RoleSerializer(role, many=True)

        return http_response(status=status.HTTP_200_OK, data=serializer.data)

    # get one role
    def retrieve(self, request, pk=None):
        if pk and not is_valid_uuid(pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('role '))

        AuthUtil.is_auth(request, is_admin=True)

        if request.decoded_token is None:
            return http_response(status=status.HTTP_400_BAD_REQUEST, message=error_messages.WRONG_TOKEN)

        role = Role.objects.get(id=pk)
        serializer = RoleSerializer(role)

        return http_response(status=status.HTTP_200_OK, data=serializer.data)

    def update(self, request, pk=None):
        if pk and not is_valid_uuid(pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('role '))

        AuthUtil.is_auth(request, is_admin=True)

        if request.decoded_token is None:
            return http_response(status=status.HTTP_400_BAD_REQUEST, message=error_messages.WRONG_TOKEN)

        role = Role.objects.update(id=pk, **request.data)
        serializer = RoleSerializer(role)

        return http_response(status=status.HTTP_200_OK, data=serializer.data)

    def delete(self, request, pk=None):
        if pk and not is_valid_uuid(pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('user '))
        AuthUtil.is_auth(request, is_admin=True)

        role = Role.objects.delete(id=pk)
        serializer = RoleSerializer(role)

        return http_response(status=status.HTTP_200_OK, data=serializer.data)
