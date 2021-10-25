from rest_framework import serializers
from bitlipa.apps.user_role.models import UserRole


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
                  'is_password_temporary',
                  'picture_url',
                  'document_type',
                  'document_front_url',
                  'document_back_url',
                  'selfie_picture_url',
                  'proof_of_residence_url',
                  'status',
                  'device_id',
                  'firebase_token',
                  'country',
                  'country_code',
                  'local_currency',
                  'initial_pin_change_date',
                  'pin_change_count',
                  'is_account_blocked',
                  'created_at',
                  'updated_at',
                  'deleted_at']

    def to_representation(self, instance):

        roles = []
        for role in UserRole.objects.filter(user=instance):
            roles.append(role.get_role())

        user_data = {
            **super().to_representation(instance),
            'roles': roles
        }
        if get_object_attr(self, 'context', {}).get('include_wallets') is True:

            user_data = {
                **user_data,
                'fiat_wallets': FiatWallet.objects.filter(user=instance).values(),
                'crypto_wallets': CryptoWallet.objects.filter(user=instance, is_master=False).values(),
            }
        return user_data


class BasicUserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ['id',
                  'first_name',
                  'middle_name',
                  'last_name',
                  'phonenumber',
                  'email',
                  'country',
                  'picture_url',
                  'document_type',
                  'document_front_url',
                  'document_back_url',
                  'selfie_picture_url',
                  'proof_of_residence_url',
                  'status',
                  'is_account_verified',
                  'initial_pin_change_date',
                  'pin_change_count',
                  'is_account_blocked', ]

    def to_representation(self, instance):
        wallet_fields = ['id', 'name', 'type', 'wallet_id', 'currency', 'address', 'description', 'logo_url']
        return{
            **super().to_representation(instance),
            'fiat_wallets': FiatWallet.objects.filter(user=instance).values(),
            'roles': UserRole.objects.filter(user=instance).values(),
            'crypto_wallets': CryptoWallet.objects.filter(user=instance, is_master=False).values(*wallet_fields)
        } if get_object_attr(self, 'context', {}).get('include_wallets') is True else super().to_representation(instance)
