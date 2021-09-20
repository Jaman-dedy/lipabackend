from rest_framework import serializers

from bitlipa.utils.get_object_attr import get_object_attr
from bitlipa.apps.users.models import User
from bitlipa.apps.fiat_wallet.models import FiatWallet
from bitlipa.apps.crypto_wallets.models import CryptoWallet


class UserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ['id',
                  'first_name',
                  'middle_name',
                  'last_name',
                  'phonenumber',
                  'email',
                  'is_admin',
                  'is_email_verified',
                  'is_phone_verified',
                  'is_account_verified',
                  'selfie_picture_url',
                  'document_url',
                  'status',
                  'device_id',
                  'firebase_token',
                  'country',
                  'country_code',
                  'local_currency',
                  'created_at',
                  'updated_at',
                  'deleted_at'
                  ]

    def to_representation(self, instance):
        return {
            **super().to_representation(instance),
            'fiat_wallets': FiatWallet.objects.filter(user=instance).values(),
            'crypto_wallets': CryptoWallet.objects.filter(user=instance, is_master=False).values(),
        } if get_object_attr(self, 'context', {}).get('include_wallets') is True else super().to_representation(instance)


class BasicUserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'first_name', 'middle_name', 'last_name', 'phonenumber', 'email', 'country', 'selfie_picture_url', 'document_url', 'status', 'is_account_verified']

    def to_representation(self, instance):
        wallet_fields = ['id', 'name', 'type', 'wallet_id', 'currency', 'address', 'description', 'logo_url']
        return{
            **super().to_representation(instance),
            'fiat_wallets': FiatWallet.objects.filter(user=instance).values(),
            'crypto_wallets': CryptoWallet.objects.filter(user=instance, is_master=False).values(*wallet_fields)
        } if get_object_attr(self, 'context', {}).get('include_wallets') is True else super().to_representation(instance)
