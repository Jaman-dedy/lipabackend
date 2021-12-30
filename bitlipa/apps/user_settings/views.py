from contextlib import suppress
from rest_framework import viewsets, status
from rest_framework.decorators import action

from bitlipa.resources import error_messages
from bitlipa.utils.is_valid_uuid import is_valid_uuid
from bitlipa.utils.http_response import http_response
from bitlipa.utils.auth_util import AuthUtil
from .models import UserSetting
from .serializers import UserSettingSerializer


class UserSettingViewSet(viewsets.ViewSet):
    """
    API endpoint that allows user settings to be viewed/edited/deleted.
    """
    @action(methods=['post', 'get'], detail=False, url_path='*', url_name='create_list_user_settings')
    def create_list_user_settings(self, request):
        # list user_settings
        if request.method == 'GET':
            return self.list_user_settings(request)

        # create user_setting
        if request.method == 'POST':
            return self.create_user_setting(request)

    def create_user_setting(self, request):
        AuthUtil.is_auth(request)
        serializer = UserSettingSerializer(UserSetting.objects.create_user_setting(user=request.user, **request.data))
        return http_response(status=status.HTTP_201_CREATED, data=serializer.data)

    def list_user_settings(self, request):
        AuthUtil.is_auth(request)
        kwargs = {
            'page': str(request.GET.get('page')),
            'per_page': str(request.GET.get('per_page')),
            'name__iexact': request.GET.get('name'),
        }
        serializer = UserSettingSerializer(UserSetting.objects.list(user=request.user, **kwargs), many=True)
        return http_response(status=status.HTTP_200_OK, data=serializer.data)

    # get one user_setting
    def retrieve(self, request, pk=None):
        AuthUtil.is_auth(request)

        if pk and not is_valid_uuid(pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('user setting '))

        user_setting = UserSetting.objects.get(user=request.user, id=pk)
        serializer = UserSettingSerializer(user_setting)
        return http_response(status=status.HTTP_200_OK, data=serializer.data)

    def update(self, request, pk=None):
        AuthUtil.is_auth(request)

        if pk and not is_valid_uuid(pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('user setting '))

        with suppress(Exception):
            request.data.pop('id')

        user_setting = UserSetting.objects.update(user=request.user, id=pk, **request.data)
        serializer = UserSettingSerializer(user_setting)

        return http_response(status=status.HTTP_200_OK, data=serializer.data)

    def delete(self, request, pk=None):
        AuthUtil.is_auth(request)

        if pk and not is_valid_uuid(pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('user setting '))

        user_setting = UserSetting.objects.remove(user=request.user, id=pk)
        serializer = UserSettingSerializer(user_setting)
        return http_response(status=status.HTTP_200_OK, data=serializer.data)
