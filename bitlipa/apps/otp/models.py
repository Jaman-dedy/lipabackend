from uuid import uuid4
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import OTPManager


class OTP(models.Model):
    class OTPDestinations(models.TextChoices):
        SMS = 'SMS', _('Send on SMS')
        EMAIL = 'EMAIL', _('Send on email')

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    phonenumber = models.CharField(verbose_name=_("phone number"), max_length=15, blank=True, null=True)
    email = models.EmailField(verbose_name=_("email"), blank=True, null=True)
    otp = models.CharField(verbose_name=_("verification code"), max_length=6, blank=False, null=False)
    destination = models.CharField(
        verbose_name=_("destination of the verification code"),
        max_length=6,
        choices=OTPDestinations.choices,
        default=OTPDestinations.SMS,
        blank=False,
        null=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_("created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("updated at"))

    objects = OTPManager()

    class Meta:
        db_table = "otp"
        ordering = ("updated_at", "created_at")

    def __str__(self):
        return self.otp
