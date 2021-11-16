import moneyed
from django.db import models
from bitlipa.resources import error_messages
from django.core.exceptions import ValidationError

from bitlipa.utils.to_decimal import to_decimal
from bitlipa.utils.format_number import format_number
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
        (rate, amount, fx_fee, errors) = (0, 0, 0, {})
        errors['base_currency'] = error_messages.REQUIRED.format('base currency is ') if not kwargs.get('base_currency') else None
        errors['currency'] = error_messages.REQUIRED.format('currency is ') if not kwargs.get('currency') else None
        errors['amount'] = error_messages.REQUIRED.format('amount is ') if not kwargs.get('amount') else None

        if len(remove_dict_none_values(errors)) != 0:
            raise ValidationError(str(errors))

        currency_exchange_fee = Fee.objects.get_fee(name__iexact="currency exchange")

        if str(currency_exchange_fee.type).upper() == str(Fee.Types.FLAT):
            fx_fee = currency_exchange_fee.amount

        if str(currency_exchange_fee.type).upper() == str(Fee.Types.PERCENTAGE):
            fx_fee = to_decimal((currency_exchange_fee.amount * to_decimal(kwargs.get('amount'))) / 100)

        source_amount = to_decimal(kwargs.get('amount')) - fx_fee
        total_source_amount = to_decimal(kwargs.get('amount'))

        try:
            currency_exchange = self.model.objects.get(base_currency=kwargs.get('base_currency'), currency=kwargs.get('currency'))
            rate = currency_exchange.rate.amount
            amount = (source_amount * currency_exchange.rate.amount) / currency_exchange.base_amount.amount
            total_amount = (total_source_amount * currency_exchange.rate.amount) / currency_exchange.base_amount.amount
        except self.model.DoesNotExist:
            try:
                currency_exchange = self.model.objects.get(base_currency=kwargs.get('currency'), currency=kwargs.get('base_currency'))
                rate = currency_exchange.rate.amount
                amount = (source_amount * currency_exchange.base_amount.amount) / currency_exchange.rate.amount
                total_amount = (total_source_amount * currency_exchange.base_amount.amount) / currency_exchange.rate.amount
            except self.model.DoesNotExist:
                # convert to default currency(USD)
                currency_exchange = self.model.objects.get(base_currency=moneyed.USD, currency=kwargs.get('base_currency'))
                amount = (source_amount * currency_exchange.base_amount.amount) / currency_exchange.rate.amount
                total_amount = (total_source_amount * currency_exchange.base_amount.amount) / currency_exchange.rate.amount

                # convert from default currency to target currency
                currency_exchange = self.model.objects.get(base_currency=moneyed.USD, currency=kwargs.get('currency'))
                amount = (to_decimal(amount) * currency_exchange.rate.amount) / currency_exchange.base_amount.amount
                total_amount = (to_decimal(total_amount) * currency_exchange.rate.amount) / currency_exchange.base_amount.amount
                rate = total_amount / total_source_amount

        return {
            'base_currency': kwargs.get('base_currency'),
            'currency': kwargs.get('currency'),
            'source_amount': format_number(source_amount),
            'total_source_amount': format_number(total_source_amount),
            'fee': format_number(fx_fee),
            'rate': format_number(rate),
            'amount': format_number(amount),
            'total_amount': format_number(total_amount),
            'date': currency_exchange.date,
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
