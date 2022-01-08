from django.db import models
from uuid import uuid4
from django.utils.translation import gettext_lazy as _


from bitlipa.apps.users.models import User
from .managers import UserActivityManager


class UserActivity(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    title = models.CharField(verbose_name=_("title"), max_length=30, blank=True, null=True)
    description = models.CharField(verbose_name=_("description"), max_length=255, blank=True, null=True,)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_("created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("updated at"))
    deleted_at = models.DateTimeField(auto_now=False, verbose_name=_("deleted at"), null=True)

    objects = UserActivityManager()

    class Meta:
        db_table = "user_activity"
        ordering = ("user_id", "title", "description")
