from rest_framework import serializers

from bitlipa.apps.users.serializers import UserSerializer
from bitlipa.apps.crypto_wallets.models import CryptoWallet


class CryptoWalletSerializer(serializers.HyperlinkedModelSerializer):
    user = UserSerializer()

    class Meta:
        model = CryptoWallet
        fields = ['id',
                  'user_id',
                  'user',
                  'name',
                  'type',
                  'wallet_id',
                  'order_id_prefix',
                  'currency',
                  'balance',
                  'address',
                  'description',
                  'logo_url',
                  'is_master',
                  'created_at',
                  'updated_at', ]
