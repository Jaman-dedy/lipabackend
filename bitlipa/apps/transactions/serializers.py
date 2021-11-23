from rest_framework import serializers

from bitlipa.apps.transactions.models import Transaction
from bitlipa.apps.users.serializers import BasicUserSerializer
from bitlipa.utils.get_object_attr import get_object_attr


class TransactionSerializer(serializers.HyperlinkedModelSerializer):
    def __init__(self, instance=None, fields=None, data=..., **kwargs):
        if data and get_object_attr(data, 'is_valid', (lambda _=None: False))():
            super().__init__(instance=instance, data=data, **kwargs)
        else:
            super().__init__(instance=instance, **kwargs)
        if fields:
            (allowed, existing) = (set(fields), set(self.fields.keys()))
            for field_name in existing - allowed:
                self.fields.pop(field_name)

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
