from rest_framework import viewsets, status
from rest_framework.decorators import action

from .models import FiatWallet, FiatWalletManager
from .serializers import FiatWalletSerializer
from bitlipa.utils.is_valid_uuid import is_valid_uuid
from bitlipa.utils.get_object_attr import get_object_attr
from bitlipa.utils.http_response import http_response
from bitlipa.resources import error_messages, success_messages
from bitlipa.utils.jwt_util import JWTUtil
from bitlipa.utils.is_auth import is_auth


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
        is_auth(request)
        token = request.headers.get("Authorization", default="").replace('Bearer', '').strip()
        decoded_token = JWTUtil.decode(token)
        serializer = FiatWalletSerializer(FiatWallet.objects.create_wallet(decoded_token, **request.data))

        return http_response(status=status.HTTP_201_CREATED, data=serializer.data)

    def list_wallets(self, request):
        is_auth(request)

        fiat_wallet = FiatWallet.objects.all().order_by('-created_at')
        serializer = FiatWalletSerializer(fiat_wallet, many=True)

        return http_response(status=status.HTTP_200_OK, data=serializer.data)

    # get one wallet
    def retrieve(self, request, pk=None):
        if pk and not is_valid_uuid(pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('wallet '))

        is_auth(request)
        token = request.headers.get("Authorization", default="").replace('Bearer', '').strip()
        decoded_token = JWTUtil.decode(token)

        if decoded_token is None:
            return http_response(status=status.HTTP_400_BAD_REQUEST, message=error_messages.WRONG_TOKEN)

        fiat_wallet = FiatWallet.objects.get(id=pk)
        serializer = FiatWalletSerializer(fiat_wallet)

        return http_response(status=status.HTTP_200_OK, data=serializer.data)

    def update(self, request, pk=None):
        if pk and not is_valid_uuid(pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('wallet '))

        is_auth(request)
        token = request.headers.get("Authorization", default="").replace('Bearer', '').strip()
        decoded_token = JWTUtil.decode(token)

        if decoded_token is None:
            return http_response(status=status.HTTP_400_BAD_REQUEST, message=error_messages.WRONG_TOKEN)

        fiat_wallet = FiatWallet.objects.update(id=pk, **request.data)
        serializer = FiatWalletSerializer(fiat_wallet)

        return http_response(status=status.HTTP_200_OK, data=serializer.data)

    def delete(self, request, pk=None):
        if pk and not is_valid_uuid(pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('user '))
        is_auth(request)

        fiat_wallet = FiatWallet.objects.delete(id=pk)
        serializer = FiatWalletSerializer(fiat_wallet)

        return http_response(status=status.HTTP_200_OK, data=serializer.data)
