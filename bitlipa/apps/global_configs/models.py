from contextlib import suppress
from django.db import models
from uuid import uuid4
from django.utils.translation import gettext_lazy as _

from .managers import GlobalConfigManager


class GlobalConfig(models.Model):
    def set_data(self, val):
        self._data = val

    def get_data(self):
        with suppress(Exception):
            return eval(self._data)
        return self._data

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(verbose_name=_("name"), max_length=30, blank=False, null=False)
    _data = models.TextField(verbose_name=_("data"), blank=True, null=True)
    data = property(get_data, set_data)
    description = models.TextField(verbose_name=_("description"), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_("created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("updated at"))
    deleted_at = models.DateTimeField(auto_now=False, verbose_name=_("deleted at"), null=True)

    objects = GlobalConfigManager()

    def __str__(self):
        return self._data

    class Meta:
        db_table = "global_configs"
        ordering = ("created_at", "updated_at")
        constraints = [
            models.UniqueConstraint(fields=['name'], name='unique_global_config')
        ]
