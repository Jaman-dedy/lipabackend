from django.conf import settings
from rest_framework import status
from contextlib import suppress
import moneyed

from bitlipa.utils.logger import logger
from bitlipa.utils.http_request import http_request
from .models import CurrencyExchange


def update_exchange_rates(force_update=False):
    if force_update is False and settings.DEBUG is True:
        # logger('update exchange rates', 'info')
        return

    response = http_request(
        url=f'{settings.FIXER_RAPID_API_URL}/latest',
        method='GET',
        params={"base": moneyed.USD},
        headers={
            'x-rapidapi-key': settings.FIXER_RAPID_API_KEY,
            'x-rapidapi-host': settings.FIXER_RAPID_API_HOST
        }
    )

    if not status.is_success(response.status_code):
        # logger(str(response.json()), 'info')
        return response.json()

    (result, exchange_rates) = (response.json(), [])
    (rates, base_currency, rates_date) = (result.get('rates'), result.get('base'), result.get('date'))

    for key in rates:
        with suppress(moneyed.CurrencyDoesNotExist, KeyError):
            moneyed.get_currency(key)
            currency_exchange = CurrencyExchange()
            currency_exchange.base_currency = base_currency
            currency_exchange.currency = key
            currency_exchange.base_amount = 1
            currency_exchange.rate = rates.get(key)
            currency_exchange.date = rates_date
            exchange_rates.append(currency_exchange)

    with suppress(Exception):
        CurrencyExchange.objects.all().delete()
        CurrencyExchange.objects.bulk_create(exchange_rates)

    return result
