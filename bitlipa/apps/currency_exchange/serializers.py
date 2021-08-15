from rest_framework import serializers

from bitlipa.apps.currency_exchange.models import CurrencyExchange


class CurrencyExchangeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CurrencyExchange
        fields = ['id', 'base_currency', 'currency', 'base_amount', 'rate', 'date']
