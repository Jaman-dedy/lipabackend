from rest_framework import serializers

from bitlipa.apps.users.serializers import BasicUserSerializer
from bitlipa.apps.loans.models import Loan


class LoanSerializer(serializers.HyperlinkedModelSerializer):

    beneficiary = BasicUserSerializer(context={'include_wallets': True})

    class Meta:
        model = Loan
        fields = [
            'id',
            'beneficiary',
            'currency',
            'limit_amount',
            'borrowed_amount',
            'description',
            'created_at',
            'updated_at',
            'deleted_at'
        ]
