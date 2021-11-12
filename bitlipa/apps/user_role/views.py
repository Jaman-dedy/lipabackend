from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.decorators import action

from .models import UserRole
from .serializers import UserRoleSerializer
from bitlipa.utils.is_valid_uuid import is_valid_uuid
from bitlipa.utils.http_response import http_response
from bitlipa.resources import error_messages
from bitlipa.utils.auth_util import AuthUtil


class UserRoleViewSet(viewsets.ViewSet):
    """
    API endpoint that allows User-role to be viewed/edited/deleted.
    """
    @action(methods=['get'], detail=False, url_path='*', url_name='list_user_roles')
    def list_user_roles(self, request):
        AuthUtil.is_auth(request)

        user_roles = UserRole.objects.all()
        serializer = UserRoleSerializer(user_roles, many=True)

        return http_response(status=status.HTTP_200_OK, data=serializer.data)

    @action(methods=['post'], detail=False, url_path='assign', url_name='assign')
    def assign_role(self, request):
        AuthUtil.is_auth(request)

        serializer = UserRoleSerializer(UserRole.objects.assign_role(**request.data), context={'include_user_roles': True})

        return http_response(status=status.HTTP_201_CREATED, data=serializer.data)

    # get role by user
    def retrieve(self, request):
        user_pk = request.data.user
        if user_pk and not is_valid_uuid(user_pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('user '))

        AuthUtil.is_auth(request)

        if request.decoded_token is None:
            return http_response(status=status.HTTP_400_BAD_REQUEST, message=error_messages.WRONG_TOKEN)

        user_role = UserRole.objects.filter(user=user_pk)
        serializer = UserRoleSerializer(user_role)

        return http_response(status=status.HTTP_200_OK, data=serializer.data)

    @action(methods=['delete'], detail=False, url_path='revoke', url_name='revoke')
    def delete(self, request):
        role_pk = request.data.get('role_id')
        user_pk = request.data.get('user_id')
        if role_pk and not is_valid_uuid(role_pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('role '))
        if user_pk and not is_valid_uuid(user_pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('user '))

        AuthUtil.is_auth(request)

        UserRole.objects.get(role_id=role_pk, user_id=user_pk).delete()

        return http_response(status=status.HTTP_200_OK, message="User role revoked with success")
