from rest_framework import viewsets, status
from rest_framework.decorators import action

from bitlipa.resources import error_messages
from bitlipa.utils.is_valid_uuid import is_valid_uuid
from bitlipa.utils.http_response import http_response
from bitlipa.utils.auth_util import AuthUtil
from .models import Fee
from .serializers import FeeSerializer


class WalletViewSet(viewsets.ViewSet):
    """
    API endpoint that allows fees to be viewed/edited/deleted.
    """
    @action(methods=['post', 'get'], detail=False, url_path='*', url_name='create_list_fees')
    def create_list_fees(self, request):
        # list fees
        if request.method == 'GET':
            return self.list_fees(request)

        # create fee
        if request.method == 'POST':
            return self.create_fee(request)

    def create_fee(self, request):
        AuthUtil.is_auth(request, is_admin=True)
        serializer = FeeSerializer(Fee.objects.create_fee(**request.data))
        return http_response(status=status.HTTP_201_CREATED, data=serializer.data)

    def list_fees(self, request):
        AuthUtil.is_auth(request, is_admin=True)
        kwargs = {
            'page': str(request.GET.get('page')),
            'per_page': str(request.GET.get('per_page')),
            'name__iexact': request.GET.get('name'),
            'type__iexact': request.GET.get('type'),
        }
        result = Fee.objects.list(**kwargs)
        serializer = FeeSerializer(result.get('data'), many=True)
        return http_response(status=status.HTTP_200_OK, data=serializer.data, meta=result.get('meta'))

    # get one fee
    def retrieve(self, request, pk=None):
        AuthUtil.is_auth(request, is_admin=True)

        if pk and not is_valid_uuid(pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('fee '))

        fee = Fee.objects.get(id=pk)
        serializer = FeeSerializer(fee)
        return http_response(status=status.HTTP_200_OK, data=serializer.data)

    def update(self, request, pk=None):
        AuthUtil.is_auth(request, is_admin=True)

        if pk and not is_valid_uuid(pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('fee '))

        fee = Fee.objects.update(id=pk, **request.data)
        serializer = FeeSerializer(fee)

        return http_response(status=status.HTTP_200_OK, data=serializer.data)

    def delete(self, request, pk=None):
        AuthUtil.is_auth(request, is_admin=True)

        if pk and not is_valid_uuid(pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('fee '))

        fee = Fee.objects.remove(id=pk)
        serializer = FeeSerializer(fee)
        return http_response(status=status.HTTP_200_OK, data=serializer.data)
