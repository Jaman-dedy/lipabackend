from rest_framework import serializers

from bitlipa.apps.transaction_limits.models import TransactionLimit


class TransactionLimitSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = TransactionLimit
        fields = ['id',
                  'currency',
                  'min_amount',
                  'max_amount',
                  'country',
                  'country_code',
                  'description',
                  'created_at',
                  'updated_at',
                  'deleted_at']
