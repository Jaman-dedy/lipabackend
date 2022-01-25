import datetime
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.db import models


from bitlipa.resources import constants
from bitlipa.resources import error_messages
from bitlipa.utils.to_int import to_int
from bitlipa.utils.to_decimal import to_decimal
from bitlipa.utils.remove_dict_none_values import remove_dict_none_values
from bitlipa.apps.users.models import User
from bitlipa.apps.global_configs.models import GlobalConfig
from bitlipa.apps.fiat_wallets.models import FiatWallet
from bitlipa.apps.users.serializers import BasicUserSerializer


class LoanManager(models.Manager):
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

    def create_loan(self, **kwargs):
        (loan, errors) = (self.model(), {})
        errors['beneficiary'] = error_messages.REQUIRED.format('loan beneficiary is ') if not kwargs.get('beneficiary_id') else None
        errors['limit_amount'] = error_messages.REQUIRED.format('loan limit amount is ') if not kwargs.get('limit_amount') else None

        beneficiary = BasicUserSerializer(User.objects.get(id=kwargs.get('beneficiary_id')), context={'include_wallets': True}).data

        if len(remove_dict_none_values(errors)) != 0:
            raise ValidationError(str(errors))

        currency = kwargs.get('currency')
        base_currency = GlobalConfig.objects.filter(name__iexact='base currency').first()
        supported_currencies = GlobalConfig.objects.filter(name__iexact='supported currencies').first()

        if str(currency).upper() not in list(map(str.upper, supported_currencies.data)):
            currency = base_currency

        loan.beneficiary_id = beneficiary.get('id')
        loan.currency = currency
        loan.limit_amount = kwargs.get('limit_amount')
        loan.borrowed_amount = kwargs.get('borrowed_amount')
        loan.description = kwargs.get('description')

        if len(beneficiary.get('fiat_wallets')):
            fiat_wallet = FiatWallet()
            fiat_wallet.name = 'Loan wallet'
            fiat_wallet.number = f'{beneficiary.get("phonenumber")}-{currency}-{len(beneficiary.get("fiat_wallets"))}'
            fiat_wallet.currency = loan.currency
            fiat_wallet.user_id = loan.beneficiary_id
            fiat_wallet.save()

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
        loan = self.model.objects.get(id=id, deleted_at=None)

        if len(remove_dict_none_values(errors)) != 0:
            raise ValidationError(str(errors))

        currency = kwargs.get('currency', loan.currency)
        base_currency = GlobalConfig.objects.filter(name__iexact='base currency').first()
        supported_currencies = GlobalConfig.objects.filter(name__iexact='supported currencies').first()

        if str(currency).upper() not in list(map(str.upper, supported_currencies.data)):
            currency = base_currency

        loan.currency = currency
        loan.limit_amount = kwargs.get('limit_amount', loan.limit_amount)
        loan.description = kwargs.get('description', loan.description)

        loan.save(using=self._db)
        return loan

    def remove(self, id=None):
        loan = self.model.objects.get(id=id, deleted_at=None)
        loan.deleted_at = datetime.datetime.now()
        loan.save(using=self._db)
        return loan
