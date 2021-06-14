from uuid import uuid4
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    first_name = models.CharField(verbose_name=_("first name"), max_length=30, blank=True, null=True)
    middle_name = models.CharField(verbose_name=_("middle name"), max_length=30, blank=True, null=True)
    last_name = models.CharField(verbose_name=_("last name"), max_length=30, blank=True, null=True)
    phonenumber = models.CharField(verbose_name=_("phone number"), max_length=15, unique=True, blank=False, null=True)
    email = models.EmailField(verbose_name=_("email"), unique=True, blank=False, null=False)
    pin = models.TextField(verbose_name=_("PIN"), blank=False, null=False)
    password = models.TextField(verbose_name=_("password"), blank=False, null=True)
    is_admin = models.BooleanField(verbose_name="is admin", blank=False, null=False, default=False)
    is_email_verified = models.BooleanField(verbose_name="is email verified", blank=False, null=False, default=False)
    is_phone_verified = models.BooleanField(verbose_name="is phone verified", blank=False, null=False, default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_("created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("updated at"))
    deleted_at = models.DateTimeField(auto_now=True, verbose_name=_("deleted at"))

    objects = UserManager()

    class Meta:
        db_table = "users"
        ordering = ("first_name", "middle_name", "last_name")

    def __str__(self):
        return self.get_full_name() or self.email

    def get_full_name(self):
        return " ".join(filter(None, [self.first_name, self.middle_name, self.last_name]))
