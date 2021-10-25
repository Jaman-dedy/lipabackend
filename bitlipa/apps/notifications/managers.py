from django.db import models
from bitlipa.resources import error_messages
import datetime
from django.core.exceptions import ValidationError
from bitlipa.utils.send_sms import send_sms


class NotificationsManager(models.Manager):
    def create_notification(self, user, **kwargs):
        notifications = self.model()

        if not kwargs.get('title'):
            raise ValidationError(error_messages.REQUIRED.format('Notification title is '))

        if not kwargs.get('content'):
            raise ValidationError(error_messages.REQUIRED.format('Notification content is '))
        if not kwargs.get('delivery_option'):
            raise ValidationError(error_messages.REQUIRED.format('Notification delivery mode is '))

        if kwargs.get('delivery_option') == 'sms':
            send_sms(kwargs.get('phonenumber'), message=kwargs.get('content'))

        notifications.sender = user
        notifications.title = kwargs.get('title')
        notifications.content = kwargs.get('content')
        notifications.delivery_option = kwargs.get('delivery_option')
        notifications.image_url = kwargs.get('image_url')

        notifications.save(using=self._db)
        return notifications

    def update(self, id=None, **kwargs):
        notifications = self.model.objects.get(id=id)

        notifications.title = kwargs.get('title') or notifications.title
        notifications.content = kwargs.get('content') or notifications.content
        notifications.delivery_option = kwargs.get('delivery_option') or notifications.delivery_option
        notifications.image_url = kwargs.get('image_url') or notifications.image_url

        notifications.save(using=self._db)
        return notifications

    def delete(self, id=None, **kwargs):
        notifications = self.model.objects.get(id=id)

        notifications.deleted_at = datetime.datetime.now()

        notifications.save(using=self._db)
        return notifications
