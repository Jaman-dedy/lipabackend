import moneyed
from django.db import models
from bitlipa.resources import error_messages
from django.core.exceptions import ValidationError

from bitlipa.utils.to_decimal import to_decimal
from bitlipa.utils.remove_dict_none_values import remove_dict_none_values
from bitlipa.apps.fees.models import Fee


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
        (rate, amount, fee, errors) = (0, 0, 0, {})
        errors['base_currency'] = error_messages.REQUIRED.format('base currency is ') if not kwargs.get('base_currency') else None
        errors['currency'] = error_messages.REQUIRED.format('currency is ') if not kwargs.get('currency') else None
        errors['amount'] = error_messages.REQUIRED.format('amount is ') if not kwargs.get('amount') else None

        if len(remove_dict_none_values(errors)) != 0:
            raise ValidationError(str(errors))

        try:
            currency_exchange = self.model.objects.get(base_currency=kwargs.get('base_currency'), currency=kwargs.get('currency'))
            rate = currency_exchange.rate.amount
            amount = (to_decimal(kwargs.get('amount')) * currency_exchange.rate.amount) / currency_exchange.base_amount.amount
        except self.model.DoesNotExist:
            try:
                currency_exchange = self.model.objects.get(base_currency=kwargs.get('currency'), currency=kwargs.get('base_currency'))
                rate = currency_exchange.rate.amount
                amount = (to_decimal(kwargs.get('amount')) * currency_exchange.base_amount.amount) / currency_exchange.rate.amount
            except self.model.DoesNotExist:
                currency_exchange_from_base_currency = self.model.objects.get(base_currency=moneyed.USD, currency=kwargs.get('base_currency'))
                amount_from_base_currency = (to_decimal(kwargs.get('amount')) * currency_exchange_from_base_currency.base_amount.amount)\
                    / currency_exchange_from_base_currency.rate.amount

                currency_exchange = self.model.objects.get(base_currency=moneyed.USD, currency=kwargs.get('currency'))
                rate = currency_exchange.rate.amount
                amount = (to_decimal(amount_from_base_currency) * currency_exchange.rate.amount) / currency_exchange.base_amount.amount

        fx_fee = Fee.objects.get_fee(name__iexact="currency exchange")
        if str(fx_fee.type).upper() == str(Fee.Types.FLAT):
            fee = fx_fee.amount

        if str(fx_fee.type).upper() == str(Fee.Types.PERCENTAGE):
            fee = to_decimal((fx_fee.amount * amount) / 100, precision=6)

        return {
            'base_currency': kwargs.get('base_currency'),
            'currency': kwargs.get('currency'),
            'rate': "{:.18f}".format(rate).rstrip('0').rstrip('.'),
            'amount': "{:.18f}".format(to_decimal(amount - fee, precision=6)).rstrip('0').rstrip('.'),
            'total_amount': "{:.18f}".format(to_decimal(amount, precision=6)).rstrip('0').rstrip('.'),
            'date': currency_exchange.date,
            'fee': "{:.18f}".format(fee).rstrip('0').rstrip('.'),
        }

    def update(self, id=None, **kwargs):
        currency_exchange = self.model.objects.get(id=id)

        currency_exchange.base_currency = kwargs.get('base_currency', currency_exchange.base_currency)
        currency_exchange.currency = kwargs.get('currency', currency_exchange.currency)
        currency_exchange.base_amount = kwargs.get('base_amount', currency_exchange.base_amount)
        currency_exchange.rate = kwargs.get('rate', currency_exchange.rate)
        currency_exchange.date = kwargs.get('date', currency_exchange.date)

        currency_exchange.save(using=self._db)
        return currency_exchange
