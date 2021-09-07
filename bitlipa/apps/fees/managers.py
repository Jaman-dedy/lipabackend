from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.db import models


from bitlipa.resources import constants
from bitlipa.resources import error_messages
from bitlipa.utils.to_int import to_int
from bitlipa.utils.remove_dict_none_values import remove_dict_none_values


class FeeManager(models.Manager):
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

    def create_fee(self, **kwargs):
        (fee, errors) = (self.model(), {})
        errors['name'] = error_messages.REQUIRED.format('fee name is ') if not kwargs.get('name') else None
        errors['type'] = error_messages.REQUIRED.format('fee type is ') if not kwargs.get('type') else None
        errors['amount'] = error_messages.REQUIRED.format('fee amount is ') if not kwargs.get('amount') else None

        if kwargs.get('type') and not (
            str(kwargs.get('type')).upper() == str(self.model.Types.FLAT)
            or str(kwargs.get('type')).upper() == str(self.model.Types.PERCENTAGE)
        ):
            errors['type'] = error_messages.INVALID_FEE_TYPE

        if len(remove_dict_none_values(errors)) != 0:
            raise ValidationError(str(errors))

        fee.name = kwargs.get('name')
        fee.type = kwargs.get('type')
        fee.currency = kwargs.get('currency')
        fee.amount = kwargs.get('amount')
        fee.description = kwargs.get('description')

        fee.save(using=self._db)
        return fee

    def update(self, id=None, **kwargs):
        errors = {}
        fee = self.model.objects.get(id=id)

        if kwargs.get('type') and not (
            str(kwargs.get('type')).upper() == str(self.model.Types.FLAT)
            or str(kwargs.get('type')).upper() == str(self.model.Types.PERCENTAGE)
        ):
            errors['type'] = error_messages.INVALID_FEE_TYPE

        if len(remove_dict_none_values(errors)) != 0:
            raise ValidationError(str(errors))

        fee.name = kwargs.get('name', fee.name)
        fee.type = kwargs.get('type', fee.type)
        fee.currency = kwargs.get('currency', fee.currency)
        fee.amount = kwargs.get('amount', fee.amount)
        fee.description = kwargs.get('description', fee.description)

        fee.save(using=self._db)
        return fee

    def remove(self, id=None):
        fee = self.model.objects.get(id=id)
        fee.delete()
        return fee
