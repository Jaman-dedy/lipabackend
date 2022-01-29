from django.db import models
from uuid import uuid4
from django.utils.translation import gettext_lazy as _

from bitlipa.apps.users.models import User
from bitlipa.apps.fiat_wallets.models import FiatWallet
from .managers import LoanManager


class Loan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    beneficiary = models.ForeignKey(User, related_name='beneficiary_id', on_delete=models.DO_NOTHING, null=False)
    wallet = models.ForeignKey(FiatWallet, related_name='loan_wallet_id', on_delete=models.DO_NOTHING, null=True)
    currency = models.CharField(verbose_name=_("currency"), max_length=30, blank=False, null=False)
    limit_amount = models.DecimalField(verbose_name=_("limit amount"),
                                       max_digits=18,
                                       decimal_places=2,
                                       blank=False,
                                       null=False,
                                       default=0)
    borrowed_amount = models.DecimalField(verbose_name=_("borrowed amount"),
                                          max_digits=18,
                                          decimal_places=2,
                                          blank=False,
                                          null=False,
                                          default=0)
    description = models.TextField(verbose_name=_("description"), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_("created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("updated at"))
    deleted_at = models.DateTimeField(auto_now=False, verbose_name=_("deleted at"), null=True)

    objects = LoanManager()

    def __str__(self):
        return self.borrowed_amount

    class Meta:
        db_table = "loans"
        ordering = ("created_at", "updated_at")
        constraints = [models.UniqueConstraint(fields=['beneficiary_id'], name='unique_loan')]
