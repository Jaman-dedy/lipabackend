from rest_framework import viewsets, status
from rest_framework.decorators import action

from bitlipa.resources import error_messages
from bitlipa.utils.is_valid_uuid import is_valid_uuid
from bitlipa.utils.http_response import http_response
from bitlipa.utils.auth_util import AuthUtil
from .models import GlobalConfig
from .serializers import GlobalConfigSerializer


class GlobalConfigSet(viewsets.ViewSet):
    """
    API endpoint that allows global configs to be viewed/edited/deleted.
    """
    @action(methods=['post', 'get'], detail=False, url_path='*', url_name='create_list_global_configs')
    def create_list_global_configs(self, request):
        # list global_configs
        if request.method == 'GET':
            return self.list_global_configs(request)

        # create global_config
        if request.method == 'POST':
            return self.create_global_config(request)

    def create_global_config(self, request):
        AuthUtil.is_auth(request, is_admin=True)
        serializer = GlobalConfigSerializer(GlobalConfig.objects.create_global_config(**request.data))
        return http_response(status=status.HTTP_201_CREATED, data=serializer.data)

    def list_global_configs(self, request):
        AuthUtil.is_auth(request, is_admin=True)
        kwargs = {
            'page': str(request.GET.get('page')),
            'per_page': str(request.GET.get('per_page')),
            'name__iexact': request.GET.get('name'),
        }
        result = GlobalConfig.objects.list(**kwargs)
        serializer = GlobalConfigSerializer(result.get('data'), many=True)
        return http_response(status=status.HTTP_200_OK, data=serializer.data, meta=result.get('meta'))

    # get one global_config
    def retrieve(self, request, pk=None):
        AuthUtil.is_auth(request, is_admin=True)

        if pk and not is_valid_uuid(pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('global config '))

        global_config = GlobalConfig.objects.get(id=pk)
        serializer = GlobalConfigSerializer(global_config)
        return http_response(status=status.HTTP_200_OK, data=serializer.data)

    def update(self, request, pk=None):
        AuthUtil.is_auth(request, is_admin=True)

        if pk and not is_valid_uuid(pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('global config '))

        global_config = GlobalConfig.objects.update(id=pk, **request.data)
        serializer = GlobalConfigSerializer(global_config)

        return http_response(status=status.HTTP_200_OK, data=serializer.data)

    def delete(self, request, pk=None):
        AuthUtil.is_auth(request, is_admin=True)

        if pk and not is_valid_uuid(pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('global config '))

        global_config = GlobalConfig.objects.remove(id=pk)
        serializer = GlobalConfigSerializer(global_config)
        return http_response(status=status.HTTP_200_OK, data=serializer.data)
