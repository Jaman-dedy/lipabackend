from django.db import models
from bitlipa.resources import error_messages
import datetime
from django.core.exceptions import ValidationError


class RoleManager(models.Manager):
    def create_role(self, **kwargs):
        role = self.model()

        if not kwargs.get('title'):
            raise ValidationError(error_messages.REQUIRED.format('role title is '))

        if not kwargs.get('description'):
            raise ValidationError(error_messages.REQUIRED.format('role description is '))
        role.title = kwargs.get('title')
        role.description = kwargs.get('description')

        role.save(using=self._db)
        return role

    def update(self, id=None, **kwargs):
        role = self.model.objects.get(id=id)

        role.title = kwargs.get('title') or role.title
        role.description = kwargs.get('description') or role.description

        role.save(using=self._db)
        return role

    def delete(self, id=None, **kwargs):
        role = self.model.objects.get(id=id)

        role.deleted_at = datetime.datetime.now()

        role.save(using=self._db)
        return role
