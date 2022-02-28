from rest_framework import viewsets, status
from rest_framework.decorators import action
from django.http import HttpResponse
from django.db import transaction as db_transaction

from bitlipa.resources import error_messages
from bitlipa.utils.is_valid_uuid import is_valid_uuid
from bitlipa.utils.http_response import http_response
from bitlipa.utils.auth_util import AuthUtil
from bitlipa.utils.logger import logger
from .models import Transaction
from .serializers import TransactionSerializer


class TransactionViewSet(viewsets.ViewSet):
    """
    API endpoints that allow transactions to be viewed/edited/deleted.
    """
    authentication_classes = []
    permission_classes = []

    @action(methods=['post', 'get'], detail=False, url_path='*', url_name='create_list_transactions')
    def create_list_transactions(self, request):
        # list transactions
        if request.method == 'GET':
            return self.list_transactions(request)

        # create transaction
        if request.method == 'POST':
            return self.create_transaction(request)

    @action(methods=['post'], detail=False, url_path='send-funds', url_name='send_funds')
    @db_transaction.atomic
    def send_funds(self, request):
        AuthUtil.is_auth(request)
        serializer = TransactionSerializer(Transaction.objects.send_funds(user=request.user, **request.data))
        return http_response(status=status.HTTP_201_CREATED, data=serializer.data)

    @action(methods=['post'], detail=False, url_path='send-crypto-funds', url_name='send_crypto_funds')
    def send_crypto_funds(self, request):
        AuthUtil.is_auth(request)
        data = Transaction.objects.send_crypto_funds(user=request.user, **request.data)
        return http_response(status=status.HTTP_201_CREATED, data=data)

    @action(methods=['post'], detail=False, url_path='topup-funds', url_name='topup_funds')
    def topup_funds(self, request):
        AuthUtil.is_auth(request)
        data = Transaction.objects.topup_funds(user=request.user, **request.data)
        return http_response(status=status.HTTP_201_CREATED, data=data)

    @action(methods=['post'], detail=False, url_path='beyonic-withdraw', url_name='beyonic_withdraw')
    @db_transaction.atomic
    def beyonic_withdraw(self, request):
        AuthUtil.is_auth(request)
        data = Transaction.objects.beyonic_withdraw(user=request.user, **request.data)
        return http_response(status=status.HTTP_201_CREATED, data=data)

    @action(methods=['post'], detail=False, url_path='confirm', url_name='confirm_transaction')
    def confirm_transaction(self, request):
        # TODO: Remove logs
        logger(request.data, 'info')
        return HttpResponse(status=status.HTTP_200_OK, content='OK')

    @action(methods=['post'], detail=False, url_path='callback', url_name='create_or_update_crypto_transaction')
    def create_or_update_crypto_transaction(self, request):
        TransactionSerializer(Transaction.objects.create_or_update_crypto_transaction(**request.data))
        return HttpResponse(status=status.HTTP_200_OK, content='OK')

    @action(methods=['post'], detail=False, url_path='topup/callback', url_name='topup_transaction')
    @db_transaction.atomic
    def create_topup_transaction(self, request):
        # TODO: Remove logs
        logger(request.data, 'info')
        TransactionSerializer(Transaction.objects.create_topup_transaction(**request.data))
        return HttpResponse(status=status.HTTP_200_OK, content='OK')

    @action(methods=['post'], detail=False, url_path='withdraw/callback', url_name='withdraw_transaction')
    @db_transaction.atomic
    def update_withdraw_transaction(self, request):
        # TODO: Remove logs
        logger(request.data, 'info')
        TransactionSerializer(Transaction.objects.update_withdraw_transaction(**request.data))
        return HttpResponse(status=status.HTTP_200_OK, content='OK')

    def list_transactions(self, request):
        AuthUtil.is_auth(request)
        kwargs = {
            'page': request.GET.get('page'),
            'per_page': request.GET.get('per_page'),
            'type__iexact': request.GET.get('type'),
            'source_currency__iexact': request.GET.get('source_currency'),
            'target_currency__iexact': request.GET.get('target_currency'),
            'state__iexact': request.GET.get('state'),
            'transaction_id': request.GET.get('transaction_id'),
            'serial': request.GET.get('serial'),
            'source_address': request.GET.get('source_address'),
            'target_address': request.GET.get('target_address'),
            'user_id': request.GET.get('user_id'),
        }

        result = Transaction.objects.list(user=request.user, **kwargs)
        serializer = TransactionSerializer(result.get('data'), many=True)
        return http_response(status=status.HTTP_200_OK, data=serializer.data, meta=result.get('meta'))

    @action(methods=['get'], detail=False, url_path='last-receivers', url_name='last_receivers')
    def list_last_receivers(self, request):
        AuthUtil.is_auth(request)
        kwargs = {
            'page': request.GET.get('page'),
            'per_page': request.GET.get('per_page'),
            'type__iexact': request.GET.get('type'),
            'source_currency__iexact': request.GET.get('source_currency'),
            'target_currency__iexact': request.GET.get('target_currency'),
            'state__iexact': request.GET.get('state'),
            'transaction_id': request.GET.get('transaction_id'),
            'serial': request.GET.get('serial'),
            'source_address': request.GET.get('source_address'),
            'target_address': request.GET.get('target_address'),
        }

        result = Transaction.objects.list_last_receivers(user=request.user, **kwargs)
        serializer = TransactionSerializer(result.get('data'), many=True, fields=['receiver', 'created_at'])
        return http_response(status=status.HTTP_200_OK, data=serializer.data, meta=result.get('meta'))

    # get one transaction
    def retrieve(self, request, pk=None):
        AuthUtil.is_auth(request)

        if pk and not is_valid_uuid(pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('transaction '))

        transaction = Transaction.objects.get(id=pk, user=request.user)
        serializer = TransactionSerializer(transaction)

        return http_response(status=status.HTTP_200_OK, data=serializer.data)

    def update(self, request, pk=None):
        AuthUtil.is_auth(request)

        if pk and not is_valid_uuid(pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('transaction '))

        transaction = Transaction.objects.update(id=pk, user=request.user, **request.data)
        serializer = TransactionSerializer(transaction)

        return http_response(status=status.HTTP_200_OK, data=serializer.data)

    def delete(self, request, pk=None):
        AuthUtil.is_auth(request)

        if pk and not is_valid_uuid(pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('user '))

        transaction = Transaction.objects.delete(id=pk, user=request.user)
        serializer = TransactionSerializer(transaction)

        return http_response(status=status.HTTP_200_OK, data=serializer.data)
