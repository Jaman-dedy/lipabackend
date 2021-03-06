from rest_framework import serializers

from bitlipa.apps.transaction_limits.models import TransactionLimit


class TransactionLimitSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = TransactionLimit
        fields = ['id',
                  'currency',
                  'amount',
                  'country',
                  'country_code',
                  'frequency',
                  'description',
                  'created_at',
                  'updated_at',
                  'deleted_at']
