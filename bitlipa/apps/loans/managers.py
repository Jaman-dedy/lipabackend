from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.db import models


from bitlipa.resources import constants
from bitlipa.resources import error_messages
from bitlipa.utils.to_int import to_int
from bitlipa.utils.to_decimal import to_decimal
from bitlipa.utils.remove_dict_none_values import remove_dict_none_values


class LoanManager(models.Manager):
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

    def create_loan(self, **kwargs):
        (loan, errors) = (self.model(), {})
        errors['name'] = error_messages.REQUIRED.format('loan name is ') if not kwargs.get('name') else None
        errors['type'] = error_messages.REQUIRED.format('loan type is ') if not kwargs.get('type') else None
        errors['amount'] = error_messages.REQUIRED.format('loan amount is ') if not kwargs.get('amount') else None

        if kwargs.get('type') and not (
            str(kwargs.get('type')).upper() == str(self.model.Types.FLAT)
            or str(kwargs.get('type')).upper() == str(self.model.Types.PERCENTAGE)
        ):
            errors['type'] = error_messages.INVALID_FEE_TYPE

        if len(remove_dict_none_values(errors)) != 0:
            raise ValidationError(str(errors))

        loan.name = kwargs.get('name')
        loan.type = kwargs.get('type')
        loan.currency = kwargs.get('currency')
        loan.amount = kwargs.get('amount')
        loan.description = kwargs.get('description')

        loan.save(using=self._db)
        return loan

    def get_loan(self, **kwargs):
        try:
            loan = self.model.objects.get(**kwargs)
            return loan
        except self.model.DoesNotExist:
            return self.model(amount=to_decimal(0))

    def update(self, id=None, **kwargs):
        errors = {}
        loan = self.model.objects.get(id=id)

        if kwargs.get('type') and not (
            str(kwargs.get('type')).upper() == str(self.model.Types.FLAT)
            or str(kwargs.get('type')).upper() == str(self.model.Types.PERCENTAGE)
        ):
            errors['type'] = error_messages.INVALID_FEE_TYPE

        if len(remove_dict_none_values(errors)) != 0:
            raise ValidationError(str(errors))

        loan.name = kwargs.get('name', loan.name)
        loan.type = kwargs.get('type', loan.type)
        loan.currency = kwargs.get('currency', loan.currency)
        loan.amount = kwargs.get('amount', loan.amount)
        loan.description = kwargs.get('description', loan.description)

        loan.save(using=self._db)
        return loan

    def remove(self, id=None):
        loan = self.model.objects.get(id=id)
        loan.delete()
        return loan
