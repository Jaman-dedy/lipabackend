from django.db import models
from uuid import uuid4
from django.utils.translation import gettext_lazy as _


from bitlipa.apps.users.models import User
from .managers import NotificationsManager


class Notification(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    sender = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    recipient = models.ForeignKey(User, related_name='recipient_id', on_delete=models.DO_NOTHING, null=True)
    title = models.CharField(verbose_name=_("title"), max_length=100, blank=True, null=True)
    content = models.CharField(verbose_name=_("content"), max_length=255, blank=True, null=True,)
    delivery_option = models.CharField(verbose_name=_("delivery_mode"), max_length=30, blank=True, null=True)
    image_url = models.CharField(verbose_name=_("image"), max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_("created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("updated at"))
    deleted_at = models.DateTimeField(auto_now=False, verbose_name=_("deleted at"), null=True)

    objects = NotificationsManager()

    class Meta:
        db_table = "notifications"
        ordering = ("created_at", "updated_at", "title", "content")
