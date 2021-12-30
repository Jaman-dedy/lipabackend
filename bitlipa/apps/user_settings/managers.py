from django.core.exceptions import ValidationError
from django.db import models


from bitlipa.resources import error_messages
from bitlipa.utils.get_object_attr import get_object_attr
from bitlipa.utils.remove_dict_none_values import remove_dict_none_values


class UserSettingManager(models.Manager):
    def list(self, user, **kwargs):
        table_fields = {**kwargs, 'user_id': get_object_attr(user, 'id'), 'deleted_at': None}

        for key in ['page', 'per_page']:
            table_fields.pop(key, None)  # remove fields not in the DB table

        return self.model.objects.filter(**remove_dict_none_values(table_fields)).order_by('-created_at')

    def create_user_setting(self, user, **kwargs):
        (user_setting, errors) = (self.model(), {})
        errors['name'] = error_messages.REQUIRED.format('user setting name is ') if not kwargs.get('name') else None
        errors['data'] = error_messages.REQUIRED.format('user setting data is ') if not kwargs.get('data') else None

        if len(remove_dict_none_values(errors)) != 0:
            raise ValidationError(str(errors))

        user_setting.name = kwargs.get('name')
        user_setting.data = kwargs.get('data')
        user_setting.description = kwargs.get('description')
        user_setting.user = user

        user_setting.save(using=self._db)
        return user_setting

    def update(self, user, id=None, **kwargs):
        user_setting = self.model.objects.get(user=user, id=id)

        user_setting.name = kwargs.get('name') or user_setting.name
        user_setting.data = kwargs.get('data', user_setting.data)
        user_setting.description = kwargs.get('description', user_setting.description)

        user_setting.save(using=self._db)
        return user_setting

    def remove(self, user, id=None):
        user_setting = self.model.objects.get(user=user, id=id)
        user_setting.delete()
        return user_setting
