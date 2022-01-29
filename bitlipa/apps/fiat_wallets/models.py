from djmoney.models.fields import MoneyField
from django.db import models
from uuid import uuid4
from django.utils.translation import gettext_lazy as _
import moneyed

from bitlipa.utils.get_object_attr import get_object_attr
from .managers import FiatWalletManager
from bitlipa.apps.users.models import User
from bitlipa.apps.currency_exchange.models import CurrencyExchange
from bitlipa.apps.global_configs.models import GlobalConfig


class FiatWalletTypes(models.TextChoices):
    PERSONAL = 'PERSONAL', _('Personal wallet')
    LOAN = 'LOAN', _('Loan wallet')
    SAVING = 'SAVING', _('Saving wallet')


class FiatWallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(verbose_name=_("wallet name"), max_length=30, blank=True, null=True)
    type = models.CharField(verbose_name=_("wallet type"),
                            max_length=10,
                            choices=FiatWalletTypes.choices,
                            default=FiatWalletTypes.PERSONAL,
                            blank=False,
                            null=False)
    number = models.CharField(verbose_name=_("wallet number"), max_length=30, blank=True, null=True, unique=True,)
    currency = models.CharField(verbose_name=_("wallet currency"), max_length=30, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_("created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("updated at"))
    deleted_at = models.DateTimeField(auto_now=False, verbose_name=_("deleted at"), null=True)
    balance = MoneyField(verbose_name=_("wallet balance"),
                         blank=False,
                         null=False,
                         default=0,
                         max_digits=18,
                         decimal_places=2,
                         currency_field_name='currency')
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)

    objects = FiatWalletManager()

    @property
    def balance_in_usd(self):
        if self.currency == moneyed.USD or not self.balance.amount:
            return self.balance.amount

        try:
            return CurrencyExchange.objects.convert(**{
                'amount': self.balance.amount,
                'base_currency': self.currency,
                'currency': moneyed.USD,
                'decimal_places': 2
            }).get('total_amount')
        except CurrencyExchange.DoesNotExist:
            return self.balance.amount

    @property
    def balance_in_local_currency(self):
        local_currency = get_object_attr(self.user, 'local_currency')

        if not local_currency or self.currency == local_currency or not self.balance.amount:
            return self.balance.amount

        try:
            return CurrencyExchange.objects.convert(**{
                'amount': self.balance.amount,
                'base_currency': self.currency,
                'currency': local_currency,
                'decimal_places': 2
            }).get('total_amount')
        except CurrencyExchange.DoesNotExist:
            return self.balance.amount

    def create_default(self, user):
        (wallet, currency, local_currency) = (None, '', '')

        base_currency = GlobalConfig.objects.filter(name__iexact='base currency').first()
        supported_currencies = GlobalConfig.objects.filter(name__iexact='supported currencies').first()

        if user.country_code:
            country_currencies = moneyed.get_currencies_of_country(user.country_code)
            if len(country_currencies) > 0:
                local_currency = moneyed.get_currencies_of_country(user.country_code)[0]

        if local_currency \
                and isinstance(get_object_attr(supported_currencies, 'data'), list) \
                and str(local_currency).upper() in list(map(str.upper, supported_currencies.data)):
            currency = str(local_currency).upper()

        if not currency and get_object_attr(base_currency, 'data'):
            currency = base_currency.data

        if currency:
            wallet = self.objects.create_wallet(user=user, **{'name': 'Personal', 'currency': currency})

        return wallet

    class Meta:
        db_table = "fiat_wallets"
        ordering = ("name", "currency", "number")
