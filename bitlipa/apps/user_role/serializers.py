from rest_framework import serializers

from bitlipa.apps.users.serializers import BasicUserSerializer
from bitlipa.apps.roles.serializers import RoleSerializer
from .models import UserRole


class UserRoleSerializer(serializers.HyperlinkedModelSerializer):
    user = BasicUserSerializer()
    role = RoleSerializer()

    class Meta:
        model = UserRole
        fields = ['id', 'user_id', 'role_id', 'user', 'role']
