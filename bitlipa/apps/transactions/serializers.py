from rest_framework import serializers

from bitlipa.apps.transactions.models import Transaction
from bitlipa.apps.users.serializers import UserSerializer


class TransactionSerializer(serializers.HyperlinkedModelSerializer):

    (sender, receiver) = (UserSerializer(data = {'include_wallets': False}), 
                          UserSerializer(data = {'include_wallets': False}))

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
                  'currency',
                  'fees',
                  'amount',
                  'total_amount',
                  'from_address',
                  'to_address',
                  'description',
                  'state',
                  'created_at',
                  'updated_at', ]
