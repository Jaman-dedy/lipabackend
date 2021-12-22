from rest_framework import serializers

from bitlipa.apps.fiat_wallets.models import FiatWallet


class FiatWalletSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FiatWallet
        fields = ['id', 'name', 'currency', 'number', 'balance', 'balance_in_usd', 'balance_in_local_currency']
