from rest_framework import serializers

from bitlipa.apps.crypto_wallets.models import CryptoWallet


class CryptoWalletSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CryptoWallet
        fields = ['id',
                  'user_id',
                  'name',
                  'type',
                  'wallet_id',
                  'currency',
                  'balance',
                  'address',
                  'description',
                  'logo_url',
                  'is_master',
                  'created_at',
                  'updated_at', ]
