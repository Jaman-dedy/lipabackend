from django.db import models
from django.utils.translation import gettext_lazy as _


class User(models.Model):
    first_name = models.CharField(verbose_name=_("First name"), max_length=30, blank=True, null=True)
    middle_name = models.CharField(verbose_name=_("Middle name"), max_length=30, blank=True, null=True)
    last_name = models.CharField(verbose_name=_("Last name"), max_length=30, blank=True, null=True)
    phonenumber = models.CharField(verbose_name=_("Phone number"), max_length=15, unique=True)
    email = models.EmailField(verbose_name=_("Email"), unique=True)

    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. " "Unselect this instead of deleting accounts."
        ),
    )

    class Meta:
        db_table = "users"
        ordering = ("first_name", "last_name")

    def __str__(self):
        return self.get_full_name() or self.email

    def get_full_name(self):
        return " ".join(filter(None, [self.first_name, self.last_name]))
