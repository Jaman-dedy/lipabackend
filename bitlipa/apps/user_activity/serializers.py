from rest_framework import serializers

from bitlipa.apps.user_activity.models import UserActivity
from bitlipa.apps.users.serializers import BasicUserSerializer


class UserActivitySerializer(serializers.HyperlinkedModelSerializer):
    user = BasicUserSerializer()
    class Meta:
        model = UserActivity
        fields = ['id', 'user_id', 'title', 'description', 'user', 'created_at']
