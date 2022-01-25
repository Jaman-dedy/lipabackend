from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.db import models


from bitlipa.resources import constants
from bitlipa.resources import error_messages
from bitlipa.utils.to_int import to_int
from bitlipa.utils.to_decimal import to_decimal
from bitlipa.utils.remove_dict_none_values import remove_dict_none_values


class TransactionLimitManager(models.Manager):
    def list(self, **kwargs):
        page = to_int(kwargs.get('page'), 1)
        per_page = to_int(kwargs.get('per_page'), constants.DB_ITEMS_LIMIT)
        table_fields = {**kwargs, 'deleted_at': None}

        for key in ['page', 'per_page']:
            table_fields.pop(key, None)  # remove fields not in the DB table

        object_list = self.model.objects.filter(**{
            'deleted_at': None, **remove_dict_none_values(table_fields)}).order_by('-created_at')
        return {
            'data': Paginator(object_list, per_page).page(page).object_list,
            'meta': {
                'page': page,
                'per_page': per_page,
                'total': object_list.count()
            }
        }

    def create_transaction_limit(self, **kwargs):
        (transaction_limit, errors) = (self.model(), {})
        errors['max_amount'] = error_messages.REQUIRED.format('transaction limit max amount is ') if not kwargs.get('max_amount') else None

        if len(remove_dict_none_values(errors)) != 0:
            raise ValidationError(str(errors))

        transaction_limit.currency = kwargs.get('currency')
        transaction_limit.min_amount = kwargs.get('min_amount')
        transaction_limit.max_amount = kwargs.get('max_amount')
        transaction_limit.country = kwargs.get('country')
        transaction_limit.country_code = kwargs.get('country_code')
        transaction_limit.description = kwargs.get('description')

        transaction_limit.save(using=self._db)
        return transaction_limit

    def get_transaction_limit(self, **kwargs):
        try:
            transaction_limit = self.model.objects.get(**kwargs)
            return transaction_limit
        except self.model.DoesNotExist:
            return self.model(min_amount=to_decimal(0), max_amount=to_decimal(0), )

    def update(self, id=None, **kwargs):
        errors = {}
        transaction_limit = self.model.objects.get(id=id)

        if kwargs.get('type') and not (
            str(kwargs.get('type')).upper() == str(self.model.Types.FLAT)
            or str(kwargs.get('type')).upper() == str(self.model.Types.PERCENTAGE)
        ):
            errors['type'] = error_messages.INVALID_FEE_TYPE

        if len(remove_dict_none_values(errors)) != 0:
            raise ValidationError(str(errors))

        transaction_limit.currency = kwargs.get('currency', transaction_limit.currency)
        transaction_limit.min_amount = kwargs.get('min_amount', transaction_limit.min_amount)
        transaction_limit.max_amount = kwargs.get('max_amount', transaction_limit.max_amount)
        transaction_limit.country = kwargs.get('country', transaction_limit.country)
        transaction_limit.country_code = kwargs.get('country_code', transaction_limit.country_code)
        transaction_limit.description = kwargs.get('description', transaction_limit.description)

        transaction_limit.save(using=self._db)
        return transaction_limit

    def remove(self, id=None):
        transaction_limit = self.model.objects.get(id=id)
        transaction_limit.delete()
        return transaction_limit
