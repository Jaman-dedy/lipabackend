from rest_framework import serializers

from bitlipa.apps.roles.models import Role


class RoleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'title', 'description']
