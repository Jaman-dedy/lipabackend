from django.db import models
from uuid import uuid4
from django.utils.translation import gettext_lazy as _

from .managers import TransactionLimitManager


class TransactionLimit(models.Model):
    class FrequencyTypes(models.TextChoices):
        DAILY = 'DAILY', _('Daily limit')
        WEEKLY = 'WEEKLY', _('Weekly limit')
        MONTHLY = 'MONTHLY', _('Monthly limit')

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    currency = models.CharField(verbose_name=_("currency"), max_length=30, blank=True, null=True)
    amount = models.DecimalField(verbose_name=_("amount"), default=0, max_digits=19, decimal_places=4, blank=True, null=True)
    country = models.CharField(verbose_name=_("country"), max_length=100, blank=True, null=True)
    country_code = models.CharField(verbose_name=_("country code"), max_length=6, blank=True, null=True)
    frequency = models.CharField(verbose_name=_("frequency"),
                                 max_length=10,
                                 choices=FrequencyTypes.choices,
                                 default=FrequencyTypes.DAILY,
                                 blank=False,
                                 null=False)
    description = models.TextField(verbose_name=_("description"), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_("created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("updated at"))
    deleted_at = models.DateTimeField(auto_now=False, verbose_name=_("deleted at"), null=True)

    objects = TransactionLimitManager()

    def __str__(self):
        return self.amount

    class Meta:
        db_table = "transaction_limits"
        ordering = ("created_at", "updated_at")
        constraints = [
            models.UniqueConstraint(
                fields=['currency', 'amount', 'country', 'country_code', 'frequency'],
                name='unique_transaction_limit')
        ]
