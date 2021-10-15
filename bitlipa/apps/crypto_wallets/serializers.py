from rest_framework import serializers
from bitlipa.utils.get_object_attr import get_object_attr

from bitlipa.apps.users.serializers import BasicUserSerializer
from bitlipa.apps.crypto_wallets.models import CryptoWallet


class CryptoWalletSerializer(serializers.HyperlinkedModelSerializer):
    user = BasicUserSerializer(context={'include_wallets': True})

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
                  'api_token',
                  'api_secret',
                  'api_refresh_token',
                  'description',
                  'logo_url',
                  'is_master',
                  'created_at',
                  'updated_at', ]

    def to_representation(self, instance):
        result = super().to_representation(instance)
        if get_object_attr(self, 'context', {}).get('include_user') is not True:
            del result['user']
        return result


class BasicCryptoWalletSerializer(serializers.HyperlinkedModelSerializer):
    user = BasicUserSerializer(context={'include_wallets': True})

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
                  'address',
                  'description',
                  'logo_url',
                  'is_master',
                  ]

    def to_representation(self, instance):
        result = super().to_representation(instance)
        if get_object_attr(self, 'context', {}).get('include_user') is not True:
            del result['user']
        return result
