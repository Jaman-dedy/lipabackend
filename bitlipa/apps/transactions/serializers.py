from rest_framework import serializers

from bitlipa.apps.transactions.models import Transaction
from bitlipa.apps.users.serializers import BasicUserSerializer


class TransactionSerializer(serializers.HyperlinkedModelSerializer):

    (sender, receiver) = (BasicUserSerializer(), BasicUserSerializer())

    class Meta:
        model = Transaction
        fields = ['id',
                  'sender',
                  'receiver',
                  'type',
                  'wallet_id',
                  'order_id',
                  'serial',
                  'vout_index',
                  'transaction_id',
                  'source_currency',
                  'target_currency',
                  'fee',
                  'fx_fee',
                  'fx_rate',
                  'source_amount',
                  'source_total_amount',
                  'target_amount',
                  'source_address',
                  'target_address',
                  'description',
                  'state',
                  'created_at',
                  'updated_at', ]
