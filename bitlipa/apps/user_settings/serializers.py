from rest_framework import serializers

from bitlipa.apps.user_settings.models import UserSetting


class UserSettingSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = UserSetting
        fields = ['id', 'name', 'data', 'description', 'created_at', 'updated_at', 'deleted_at']
