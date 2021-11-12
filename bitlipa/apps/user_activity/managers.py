from django.db import models
from bitlipa.resources import error_messages
import datetime
from django.core.exceptions import ValidationError


class UserActivityManager(models.Manager):
    def create_user_activity(self, user, **kwargs):
        user_activity = self.model()

        if not kwargs.get('title'):
            raise ValidationError(error_messages.REQUIRED.format('Activity title is '))

        if not kwargs.get('description'):
            raise ValidationError(error_messages.REQUIRED.format('Activity description is '))

        user_activity.user = user
        user_activity.title = kwargs.get('title')
        user_activity.description = kwargs.get('description')

        user_activity.save(using=self._db)
        return user_activity

    def delete(self, id=None, **kwargs):
        user_activity = self.model.objects.get(id=id)

        user_activity.deleted_at = datetime.datetime.now()

        user_activity.save(using=self._db)
        return user_activity
