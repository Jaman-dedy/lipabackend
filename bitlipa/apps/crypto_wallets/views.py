from rest_framework import viewsets, status
from rest_framework.decorators import action

from bitlipa.resources import error_messages
from bitlipa.utils.is_valid_uuid import is_valid_uuid
from bitlipa.utils.http_response import http_response
from bitlipa.utils.auth_util import AuthUtil
from .models import CryptoWallet
from .serializers import CryptoWalletSerializer


class WalletViewSet(viewsets.ViewSet):
    """
    API endpoint that allows Crypto wallet to be viewed/edited/deleted.
    """
    @action(methods=['post', 'get'], detail=False, url_path='*', url_name='create_list_update_crypto_wallets')
    def create_list_wallets(self, request):
        # list wallets
        if request.method == 'GET':
            return self.list_wallets(request)

        # create wallet
        if request.method == 'POST':
            return self.create_wallet(request)

    def create_wallet(self, request):
        AuthUtil.is_auth(request)
        serializer = CryptoWalletSerializer(CryptoWallet.objects.create_wallet(user=request.user, **request.data))
        return http_response(status=status.HTTP_201_CREATED, data=serializer.data)

    @action(methods=['post'], detail=False, url_path='addresses', url_name='create_crypto_wallet_addresses')
    def create_wallet_address(self, request):
        AuthUtil.is_auth(request)
        serializer = CryptoWalletSerializer(CryptoWallet.objects.create_wallet_address(user=request.user, **request.data), many=True)
        return http_response(status=status.HTTP_201_CREATED, data=serializer.data)

    @action(methods=['get'], detail=False, url_path=r'addresses/(?P<wallet_id>.*)', url_name='list_crypto_wallet_addresses')
    def list_wallet_addresses(self, request, *args, **kwargs):
        AuthUtil.is_auth(request)
        response = CryptoWallet.objects.list_wallet_addresses(user=request.user, wallet_id=kwargs.get('wallet_id'))
        return http_response(status=response.get('status_code') or status.HTTP_200_OK, data=response.get('data'))

    def list_wallets(self, request):
        AuthUtil.is_auth(request)
        kwargs = {
            'page': request.GET.get('page'),
            'per_page': request.GET.get('per_page'),
            'is_master': str(request.GET.get('master')).lower() == 'true' or str(request.GET.get('master')).lower() == '1',
            'all': str(request.GET.get('all')).lower() == 'true' or str(request.GET.get('all')).lower() == '1',
            'name__iexact': request.GET.get('name'),
            'type__iexact': request.GET.get('type'),
        }

        result = CryptoWallet.objects.list(user=request.user, **kwargs)
        serializer = CryptoWalletSerializer(result.get('data'), many=True)
        return http_response(status=status.HTTP_200_OK, data=serializer.data, meta=result.get('meta'))

    # get one wallet
    def retrieve(self, request, pk=None):
        AuthUtil.is_auth(request)

        if pk and not is_valid_uuid(pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('wallet '))

        crypto_wallet = CryptoWallet.objects.get(id=pk, user=request.user)
        serializer = CryptoWalletSerializer(crypto_wallet)

        return http_response(status=status.HTTP_200_OK, data=serializer.data)

    def update(self, request, pk=None):
        AuthUtil.is_auth(request)

        if pk and not is_valid_uuid(pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('wallet '))

        crypto_wallet = CryptoWallet.objects.update(id=pk, user=request.user, **request.data)
        serializer = CryptoWalletSerializer(crypto_wallet)

        return http_response(status=status.HTTP_200_OK, data=serializer.data)

    def delete(self, request, pk=None):
        AuthUtil.is_auth(request)

        if pk and not is_valid_uuid(pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('user '))

        crypto_wallet = CryptoWallet.objects.delete(id=pk, user=request.user)
        serializer = CryptoWalletSerializer(crypto_wallet)

        return http_response(status=status.HTTP_200_OK, data=serializer.data)
