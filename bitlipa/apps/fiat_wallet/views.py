from rest_framework import viewsets, status
from rest_framework.decorators import action

from .models import FiatWallet
from .serializers import FiatWalletSerializer
from bitlipa.utils.is_valid_uuid import is_valid_uuid
from bitlipa.utils.http_response import http_response
from bitlipa.resources import error_messages
from bitlipa.utils.auth_util import AuthUtil


class WalletViewSet(viewsets.ViewSet):
    """
    API endpoint that allows Fiat wallet to be viewed/edited/deleted.
    """
    @action(methods=['post', 'get'], detail=False, url_path='*', url_name='create_list_update_wallets')
    def create_list_wallets(self, request):
        # list wallets
        if request.method == 'GET':
            return self.list_wallets(request)

        # create wallet
        if request.method == 'POST':
            return self.create_wallet(request)

    def create_wallet(self, request):
        AuthUtil.is_auth(request)

        serializer = FiatWalletSerializer(FiatWallet.objects.create_wallet(request.decoded_token, **request.data))

        return http_response(status=status.HTTP_201_CREATED, data=serializer.data)

    def list_wallets(self, request):
        AuthUtil.is_auth(request)

        fiat_wallet = FiatWallet.objects.all().order_by('-created_at')
        serializer = FiatWalletSerializer(fiat_wallet, many=True)

        return http_response(status=status.HTTP_200_OK, data=serializer.data)

    # get one wallet
    def retrieve(self, request, pk=None):
        if pk and not is_valid_uuid(pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('wallet '))

        AuthUtil.is_auth(request)

        if request.decoded_token is None:
            return http_response(status=status.HTTP_400_BAD_REQUEST, message=error_messages.WRONG_TOKEN)

        fiat_wallet = FiatWallet.objects.get(id=pk)
        serializer = FiatWalletSerializer(fiat_wallet)

        return http_response(status=status.HTTP_200_OK, data=serializer.data)

    def update(self, request, pk=None):
        if pk and not is_valid_uuid(pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('wallet '))

        AuthUtil.is_auth(request)

        if request.decoded_token is None:
            return http_response(status=status.HTTP_400_BAD_REQUEST, message=error_messages.WRONG_TOKEN)

        fiat_wallet = FiatWallet.objects.update(id=pk, **request.data)
        serializer = FiatWalletSerializer(fiat_wallet)

        return http_response(status=status.HTTP_200_OK, data=serializer.data)

    def delete(self, request, pk=None):
        if pk and not is_valid_uuid(pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('user '))
        AuthUtil.is_auth(request)

        fiat_wallet = FiatWallet.objects.delete(id=pk)
        serializer = FiatWalletSerializer(fiat_wallet)

        return http_response(status=status.HTTP_200_OK, data=serializer.data)
