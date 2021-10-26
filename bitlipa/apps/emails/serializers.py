from rest_framework import serializers

from bitlipa.apps.emails.models import Email


class EmailSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Email
        fields = ['id', 'recipients', 'body', 'created_at', 'updated_at']
