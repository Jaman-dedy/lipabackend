from django.db import models
from uuid import uuid4
from django.utils.translation import gettext_lazy as _

from .managers import FeeManager


class Fee(models.Model):
    class Types(models.TextChoices):
        FLAT = 'FLAT', _('Flat fee')
        PERCENTAGE = 'PERCENTAGE', _('Percentage fee')

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(verbose_name=_("name"), max_length=30, blank=True, null=True)
    type = models.CharField(verbose_name=_("fee type"), max_length=10, choices=Types.choices, default=Types.FLAT, blank=False, null=False)
    currency = models.CharField(verbose_name=_("currency"), max_length=30, blank=True, null=True)
    amount = models.DecimalField(verbose_name=_("amount"), max_digits=19, decimal_places=4, blank=True, null=True)
    description = models.TextField(verbose_name=_("description"), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_("created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("updated at"))
    deleted_at = models.DateTimeField(auto_now=False, verbose_name=_("deleted at"), null=True)

    objects = FeeManager()

    class Meta:
        db_table = "fees"
        ordering = ("created_at", "updated_at")
        constraints = [
            models.UniqueConstraint(fields=['name', 'type'], name='unique_fee')
        ]
