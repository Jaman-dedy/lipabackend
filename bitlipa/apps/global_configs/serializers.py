from rest_framework import serializers

from bitlipa.apps.global_configs.models import GlobalConfig


class GlobalConfigSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = GlobalConfig
        fields = ['id', 'name', 'data', 'description', 'created_at', 'updated_at', 'deleted_at']
