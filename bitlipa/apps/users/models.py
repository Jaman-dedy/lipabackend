from uuid import uuid4
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(models.Model):
    class DocumentTypes(models.TextChoices):
        ID = 'ID', _('National ID')
        PASSPORT = 'PASSPORT', _('Passport')

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
    is_account_verified = models.BooleanField(verbose_name="is account verified", blank=False, null=False, default=False)
    is_password_temporary = models.BooleanField(verbose_name="is password temporary", blank=False, null=False, default=False)
    device_id = models.CharField(verbose_name=_("Device id"), max_length=30, blank=True, null=True)
    firebase_token = models.CharField(verbose_name=_("Firebase token"), max_length=255, blank=True, null=True)
    picture_url = models.CharField(verbose_name=_("Profile picture"), max_length=255, blank=True, null=True)
    document_type = models.CharField(verbose_name=_("Document type"),
                                     max_length=10,
                                     choices=DocumentTypes.choices,
                                     default=DocumentTypes.ID,
                                     blank=False,
                                     null=False)
    document_front_url = models.CharField(verbose_name=_("Front side of ID or Passport"), max_length=255, blank=True, null=True)
    document_back_url = models.CharField(verbose_name=_("Back side of ID or Passport"), max_length=255, blank=True, null=True)
    selfie_picture_url = models.CharField(verbose_name=_("Selfie"), max_length=255, blank=True, null=True)
    proof_of_residence_url = models.CharField(verbose_name=_("Proof of residence"), max_length=255, blank=True, null=True)
    country = models.CharField(verbose_name=_("country"), max_length=100, blank=True, null=True)
    status = models.CharField(verbose_name=_("status"), max_length=100, blank=True, null=True)
    country_code = models.CharField(verbose_name=_("country code"), max_length=6, blank=True, null=True)
    local_currency = models.CharField(verbose_name=_("local currency"), max_length=6, blank=True, null=True)
    initial_pin_change_date = models.DateTimeField(auto_now=False, verbose_name=_("initial PIN change date"), null=True)
    pin_change_count = models.IntegerField(verbose_name=_("PIN change count"), blank=False, null=False, default=0)
    is_account_blocked = models.BooleanField(verbose_name="is account blocked", blank=False, null=False, default=False)
    last_wrong_login_attempt_date = models.DateTimeField(auto_now=False, verbose_name=_("last wrong login attempt date"), null=True)
    wrong_login_attempts_count = models.IntegerField(verbose_name=_("wrong login attempts count"), blank=False, null=False, default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_("created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("updated at"))
    deleted_at = models.DateTimeField(auto_now=False, verbose_name=_("deleted at"), null=True)
    creator_id = models.UUIDField(default=uuid4, editable=False, null=True, blank=True)

    objects = UserManager()

    class Meta:
        db_table = "users"
        ordering = ("created_at", "created_at")

    def __str__(self):
        return self.get_full_name() or self.email

    def get_full_name(self):
        return " ".join(filter(None, [self.first_name, self.middle_name, self.last_name]))
