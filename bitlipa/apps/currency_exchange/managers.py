from django.db import models
import moneyed
from bitlipa.resources import error_messages
from django.core.exceptions import ValidationError

from bitlipa.utils.to_decimal import to_decimal
from bitlipa.utils.remove_dict_none_values import remove_dict_none_values


class CurrencyExchangeManager(models.Manager):
    def create_exchange_rate(self, **kwargs):
        currency_exchange = self.model()
        errors = {}
        errors['currency'] = error_messages.REQUIRED.format('currency is ') if not kwargs.get('currency') else None
        errors['rate'] = error_messages.REQUIRED.format('exchange rate is ') if not kwargs.get('rate') else None

        if len(remove_dict_none_values(errors)) != 0:
            raise ValidationError(str(errors))

        currency_exchange.base_currency = kwargs.get('base_currency', moneyed.USD)
        currency_exchange.currency = kwargs.get('currency')
        currency_exchange.base_amount = kwargs.get('base_amount', 1)
        currency_exchange.rate = kwargs.get('rate', 1)
        currency_exchange.date = kwargs.get('date')

        currency_exchange.save(using=self._db)
        return currency_exchange

    def convert(self, **kwargs):
        errors = {}
        errors['base_currency'] = error_messages.REQUIRED.format('base currency is ') if not kwargs.get('base_currency') else None
        errors['currency'] = error_messages.REQUIRED.format('currency is ') if not kwargs.get('currency') else None
        errors['amount'] = error_messages.REQUIRED.format('amount is ') if not kwargs.get('amount') else None

        if len(remove_dict_none_values(errors)) != 0:
            raise ValidationError(str(errors))

        try:
            currency_exchange = self.model.objects.get(base_currency=kwargs.get('base_currency'), currency=kwargs.get('currency'))
            amount = (to_decimal(kwargs.get('amount')) * currency_exchange.rate.amount) / currency_exchange.base_amount.amount
        except self.model.DoesNotExist:
            currency_exchange = self.model.objects.get(base_currency=kwargs.get('currency'), currency=kwargs.get('base_currency'))
            amount = (to_decimal(kwargs.get('amount')) * currency_exchange.base_amount.amount) / currency_exchange.rate.amount

        result = {
            'base_currency': currency_exchange.base_currency,
            'currency': currency_exchange.currency,
            'rate': str(currency_exchange.rate.amount),
            'amount': str(to_decimal(amount, precision=6)),
            'date': currency_exchange.date,
        }
        return result

    def update(self, id=None, **kwargs):
        currency_exchange = self.model.objects.get(id=id)

        currency_exchange.base_currency = kwargs.get('base_currency', currency_exchange.base_currency)
        currency_exchange.currency = kwargs.get('currency', currency_exchange.currency)
        currency_exchange.base_amount = kwargs.get('base_amount', currency_exchange.base_amount)
        currency_exchange.rate = kwargs.get('rate', currency_exchange.rate)
        currency_exchange.date = kwargs.get('date', currency_exchange.date)

        currency_exchange.save(using=self._db)
        return currency_exchange
