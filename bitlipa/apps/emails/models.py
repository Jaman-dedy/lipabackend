from django.db import models
from django.contrib.postgres.fields import ArrayField
from uuid import uuid4
from django.utils.translation import gettext_lazy as _

from .managers import EmailManager


class Email(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    recipients = ArrayField(models.EmailField(verbose_name=_("email"), blank=False, null=False))
    body = models.TextField(verbose_name=_("body"), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_("created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("updated at"))
    deleted_at = models.DateTimeField(auto_now=False, verbose_name=_("deleted at"), null=True)

    objects = EmailManager()

    def __str__(self):
        return self.body

    class Meta:
        db_table = "emails"
        ordering = ("created_at", "updated_at")
