from rest_framework import serializers

from bitlipa.apps.users.models import User


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['id',
                  'first_name',
                  'middle_name',
                  'last_name',
                  'phonenumber',
                  'email',
                  'is_admin',
                  'is_email_verified',
                  'is_phone_verified',
                  'created_at',
                  'updated_at'
                  ]
