from rest_framework import viewsets, status
from rest_framework.decorators import action

from bitlipa.resources import error_messages
from bitlipa.utils.is_valid_uuid import is_valid_uuid
from bitlipa.utils.http_response import http_response
from bitlipa.utils.auth_util import AuthUtil
from .models import TransactionLimit
from .serializers import TransactionLimitSerializer


class TransactionLimitSet(viewsets.ViewSet):
    """
    API endpoint that allows transaction limits to be viewed/edited/deleted.
    """
    @action(methods=['post', 'get'], detail=False, url_path='*', url_name='create_list_transaction_limits')
    def create_list_transaction_limits(self, request):
        # list transaction_limits
        if request.method == 'GET':
            return self.list_transaction_limits(request)

        # create transaction_limit
        if request.method == 'POST':
            return self.create_transaction_limit(request)

    def create_transaction_limit(self, request):
        AuthUtil.is_auth(request, is_admin=True)
        serializer = TransactionLimitSerializer(TransactionLimit.objects.create_transaction_limit(**request.data))
        return http_response(status=status.HTTP_201_CREATED, data=serializer.data)

    def list_transaction_limits(self, request):
        AuthUtil.is_auth(request, is_admin=True)
        kwargs = {
            'page': str(request.GET.get('page')),
            'per_page': str(request.GET.get('per_page')),
            'min_amount__iexact': request.GET.get('min_amount'),
            'max_amount__iexact': request.GET.get('max_amount'),
            'currency__iexact': request.GET.get('currency'),
            'country__iexact': request.GET.get('country'),
            'country_code__iexact': request.GET.get('country_code'),
            'frequency__iexact': request.GET.get('frequency'),
        }
        result = TransactionLimit.objects.list(**kwargs)
        serializer = TransactionLimitSerializer(result.get('data'), many=True)
        return http_response(status=status.HTTP_200_OK, data=serializer.data, meta=result.get('meta'))

    # get one transaction_limit
    def retrieve(self, request, pk=None):
        AuthUtil.is_auth(request, is_admin=True)

        if pk and not is_valid_uuid(pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('transaction limit '))

        transaction_limit = TransactionLimit.objects.get(id=pk)
        serializer = TransactionLimitSerializer(transaction_limit)
        return http_response(status=status.HTTP_200_OK, data=serializer.data)

    def update(self, request, pk=None):
        AuthUtil.is_auth(request, is_admin=True)

        if pk and not is_valid_uuid(pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('transaction limit '))

        transaction_limit = TransactionLimit.objects.update(id=pk, **request.data)
        serializer = TransactionLimitSerializer(transaction_limit)

        return http_response(status=status.HTTP_200_OK, data=serializer.data)

    def delete(self, request, pk=None):
        AuthUtil.is_auth(request, is_admin=True)

        if pk and not is_valid_uuid(pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('transaction limit '))

        transaction_limit = TransactionLimit.objects.remove(id=pk)
        serializer = TransactionLimitSerializer(transaction_limit)
        return http_response(status=status.HTTP_200_OK, data=serializer.data)
