from bitlipa.utils.get_object_attr import get_object_attr
from rest_framework import serializers

from bitlipa.apps.users.models import User
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
                  'created_at',
                  'updated_at'
                  ]

    def to_representation(self, instance):
        return {
            **super().to_representation(instance),
            'crypto_wallets': None if get_object_attr(self, 'initial_data', {}).get('include_wallets') is False else
            CryptoWallet.objects.filter(user=instance, is_master=False).values()
        }


class BasicUserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ['id',
                  'first_name',
                  'middle_name',
                  'last_name',
                  'phonenumber',
                  'email',
                  ]

    def to_representation(self, instance):
        return {
            **super().to_representation(instance),
            'crypto_wallets': None if get_object_attr(self, 'initial_data', {}).get('include_wallets') is False else
            CryptoWallet.objects.filter(user=instance, is_master=False).values('id',
                                                                               'user_id',
                                                                               'name',
                                                                               'type',
                                                                               'wallet_id',
                                                                               'order_id_prefix',
                                                                               'currency',
                                                                               'address',
                                                                               'description',
                                                                               'logo_url',
                                                                               'is_master')
        }
