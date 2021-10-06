from django.db import models
from bitlipa.resources import error_messages
from django.core.exceptions import ValidationError
from bitlipa.apps.users.models import User
from bitlipa.apps.roles.models import Role


class UserRoleManager(models.Manager):
    def assign_role(self, **kwargs):
        user_role = self.model()

        if not kwargs.get('user_id'):
            raise ValidationError(error_messages.REQUIRED.format('user id is '))

        if not kwargs.get('role_id'):
            raise ValidationError(error_messages.REQUIRED.format('role id currency is '))

        for role_id in kwargs.get('role_id'):
            user_roles = self.model()
            user = User.objects.get(pk=kwargs.get('user_id'))
            role = Role.objects.get(pk=role_id)
            user_roles.user_id = user.id
            user_roles.role_id = role.id
            user_roles.save()

        return user_roles
