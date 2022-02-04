from rest_framework import serializers

from bitlipa.apps.notifications.models import Notification


class NotificationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id',
            'sender_id',
            'recipient_id',
            'title',
            'content',
            'delivery_option',
            'image_url',
            'status',
            'created_at'
        ]
