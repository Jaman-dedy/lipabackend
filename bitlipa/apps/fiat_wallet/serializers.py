from rest_framework import serializers

from bitlipa.apps.fiat_wallet.models import FiatWallet


class FiatWalletSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FiatWallet
        fields = ['id', 'name', 'currency', 'number', 'balance']
