from rest_framework import serializers

from bitlipa.apps.phones.models import Phone


class PhoneSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Phone
        fields = ['id', 'phonenumber', 'is_phone_verified', 'email']
