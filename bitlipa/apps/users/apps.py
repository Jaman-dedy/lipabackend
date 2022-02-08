
from django.apps import AppConfig


class UserSetting(AppConfig):
    name = "bitlipa.apps.users"

    def ready(self):
        from . import signals  # noqa
