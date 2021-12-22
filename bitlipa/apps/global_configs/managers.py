from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.db import models


from bitlipa.resources import constants
from bitlipa.resources import error_messages
from bitlipa.utils.to_int import to_int
from bitlipa.utils.remove_dict_none_values import remove_dict_none_values


class GlobalConfigManager(models.Manager):
    def list(self, **kwargs):
        page = to_int(kwargs.get('page'), 1)
        per_page = to_int(kwargs.get('per_page'), constants.DB_ITEMS_LIMIT)
        table_fields = {**kwargs, 'deleted_at': None}

        for key in ['page', 'per_page']:
            table_fields.pop(key, None)  # remove fields not in the DB table

        object_list = self.model.objects.filter(**remove_dict_none_values(table_fields)).order_by('-created_at')
        return {
            'data': Paginator(object_list, per_page).page(page).object_list,
            'meta': {
                'page': page,
                'per_page': per_page,
                'total': object_list.count()
            }
        }

    def create_global_config(self, **kwargs):
        (global_config, errors) = (self.model(), {})
        errors['name'] = error_messages.REQUIRED.format('global config name is ') if not kwargs.get('name') else None
        errors['data'] = error_messages.REQUIRED.format('global config data is ') if not kwargs.get('data') else None

        if len(remove_dict_none_values(errors)) != 0:
            raise ValidationError(str(errors))

        global_config.name = kwargs.get('name')
        global_config.data = kwargs.get('data')
        global_config.description = kwargs.get('description')

        global_config.save(using=self._db)
        return global_config

    def update(self, id=None, **kwargs):
        global_config = self.model.objects.get(id=id)

        global_config.name = kwargs.get('name') or global_config.name
        global_config.data = kwargs.get('data', global_config.data)
        global_config.description = kwargs.get('description', global_config.description)

        global_config.save(using=self._db)
        return global_config

    def remove(self, id=None):
        global_config = self.model.objects.get(id=id)
        global_config.delete()
        return global_config
