from django.db import models
from uuid import uuid4
from django.utils.translation import gettext_lazy as _

# from .managers import RoleManager


class MpesaAuth(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    access_token = models.CharField(verbose_name=_("access_token"), max_length=255, blank=True, null=True, unique=True,)
    expires_in = models.CharField(verbose_name=_("expires_in"), max_length=30, blank=True, null=True, unique=True,)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_("created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("updated at"))
    deleted_at = models.DateTimeField(auto_now=False, verbose_name=_("deleted at"), null=True)

    # objects = RoleManager()

    class Meta:
        db_table = "mpesaauth"
        ordering = ("access_token", "expires_in")