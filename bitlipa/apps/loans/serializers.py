from rest_framework import serializers

from bitlipa.apps.loans.models import Loan


class LoanSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Loan
        fields = ['id',
                  'name',
                  'type',
                  'currency',
                  'amount',
                  'description',
                  'created_at',
                  'updated_at',
                  'deleted_at']
