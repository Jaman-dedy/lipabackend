from django.db import models
from uuid import uuid4
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now

from .managers import FiatWalletManager
from bitlipa.resources import error_messages


class FiatWallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    wallet_name = models.CharField(verbose_name=_("wallet name"), max_length=30, blank=True, null=True)
    wallet_number = models.CharField(verbose_name=_("wallet number"), max_length=30, blank=True, null=True, unique=True,)
    wallet_currency = models.CharField(verbose_name=_("wallet currency"), max_length=30, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_("created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("updated at"))
    deleted_at = models.DateTimeField(auto_now=False, verbose_name=_("deleted at"), null=True)

    objects = FiatWalletManager()

    class Meta:
        db_table = "fiat_wallet"
        ordering = ("wallet_name", "wallet_number", "wallet_currency")
