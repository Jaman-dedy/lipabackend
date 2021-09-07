from rest_framework import serializers

from bitlipa.apps.fees.models import Fee


class FeeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Fee
        fields = ['id',
                  'name',
                  'type',
                  'currency',
                  'amount',
                  'description',
                  'created_at',
                  'updated_at',
                  'deleted_at']
