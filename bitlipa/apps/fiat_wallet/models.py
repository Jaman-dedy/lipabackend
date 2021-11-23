from djmoney.models.fields import MoneyField
from django.db import models
from uuid import uuid4
from django.utils.translation import gettext_lazy as _

from bitlipa.utils.get_object_attr import get_object_attr
from .managers import FiatWalletManager
from bitlipa.apps.users.models import User
from bitlipa.apps.currency_exchange.models import CurrencyExchange


class FiatWallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(verbose_name=_("wallet name"), max_length=30, blank=True, null=True)
    number = models.CharField(verbose_name=_("wallet number"), max_length=30, blank=True, null=True, unique=True,)
    currency = models.CharField(verbose_name=_("wallet currency"), max_length=30, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_("created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("updated at"))
    deleted_at = models.DateTimeField(auto_now=False, verbose_name=_("deleted at"), null=True)
    balance = MoneyField(
        verbose_name=_("wallet balance"),
        blank=False,
        null=False,
        default=0,
        max_digits=36,
        decimal_places=18,
        currency_field_name='currency'
    )
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)

    objects = FiatWalletManager()

    @property
    def balance_in_local_currency(self):
        local_currency = get_object_attr(self.user, 'local_currency')

        if not local_currency or self.currency == local_currency or not self.balance.amount:
            return self.balance.amount

        return CurrencyExchange.objects.convert(**{
            'amount': self.balance.amount,
            'base_currency': self.currency,
            'currency': local_currency ,
        }).get('total_amount')

    class Meta:
        db_table = "fiat_wallet"
        ordering = ("name", "currency", "number")
