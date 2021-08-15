from uuid import uuid4
from djmoney.models.fields import MoneyField
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import CurrencyExchangeManager


class CurrencyExchange(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    base_currency = models.CharField(verbose_name=_("from currency"), max_length=30, blank=False, null=False)
    currency = models.CharField(verbose_name=_("to currency"), max_length=30, blank=False, null=False)
    base_amount = MoneyField(
        verbose_name=_("base_amount"),
        blank=False,
        null=False,
        default=1,
        max_digits=36,
        decimal_places=18,
        currency_field_name='base_currency'
    )
    rate = MoneyField(
        verbose_name=_("exchange rate"),
        blank=False,
        null=False,
        default=1,
        max_digits=36,
        decimal_places=18,
        currency_field_name='currency'
    )
    date = models.CharField(verbose_name=_("exchange rate date"), max_length=30, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_("created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("updated at"))
    deleted_at = models.DateTimeField(auto_now=False, verbose_name=_("deleted at"), null=True)

    objects = CurrencyExchangeManager()

    class Meta:
        db_table = "currency_exchange"
        ordering = ("base_currency", "currency")
        unique_together = (('base_currency', 'currency'))
