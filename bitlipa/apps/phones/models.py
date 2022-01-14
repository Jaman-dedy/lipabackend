from django.db import models
from uuid import uuid4
from django.utils.translation import gettext_lazy as _
from django.core import serializers

from .managers import PhoneManager


class Phone(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    phonenumber = models.CharField(verbose_name=_("phone number"), max_length=15, unique=True, blank=False, null=True)
    email = models.EmailField(verbose_name=_("email"), blank=False, null=False)
    is_phone_verified = models.BooleanField(verbose_name="is phone verified", blank=False, null=False, default=False)
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("updated at"))
    deleted_at = models.DateTimeField(auto_now=False, verbose_name=_("deleted at"), null=True)

    objects = PhoneManager()

    class Meta:
        db_table = 'phone'



