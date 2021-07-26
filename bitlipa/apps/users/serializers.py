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
            'crypto_wallets': CryptoWallet.objects.filter(user=instance, is_master=False).values()
        }
