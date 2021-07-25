from djmoney.models.fields import MoneyField
from django.db import models
from uuid import uuid4
from django.utils.translation import gettext_lazy as _

from bitlipa.apps.users.models import User
from .managers import CryptoWalletManager


class CryptoWallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    name = models.CharField(verbose_name=_("wallet name"), max_length=30, blank=True, null=True)
    type = models.CharField(verbose_name=_("wallet type"), max_length=30, blank=True, null=True)
    wallet_id = models.CharField(verbose_name=_("wallet ID"), max_length=30, blank=True, null=True)
    currency = models.CharField(verbose_name=_("wallet currency"), max_length=30, blank=False, null=False)
    balance = MoneyField(
        verbose_name=_("wallet balance"),
        blank=False,
        null=False,
        default=0,
        max_digits=36,
        decimal_places=18,
        currency_field_name='currency'
    )
    address = models.CharField(verbose_name=_("wallet address"), max_length=100, blank=False, null=False, unique=True)
    description = models.TextField(verbose_name=_("wallet description"), blank=True, null=True)
    api_token = models.CharField(verbose_name=_("wallet API token"), max_length=100, blank=True, null=True)
    api_secret = models.CharField(verbose_name=_("wallet API secret"), max_length=100, blank=True, null=True)
    api_refresh_token = models.CharField(verbose_name=_("wallet API refresh token"), max_length=100, blank=True, null=True)
    logo_url = models.CharField(verbose_name=_("wallet logo"), max_length=100, blank=True, null=True)
    is_master = models.BooleanField(verbose_name="is master wallet", blank=False, null=False, default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_("created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("updated at"))
    deleted_at = models.DateTimeField(auto_now=False, verbose_name=_("deleted at"), null=True)

    objects = CryptoWalletManager()

    class Meta:
        db_table = "crypto_wallets"
        ordering = ("created_at", "updated_at")
