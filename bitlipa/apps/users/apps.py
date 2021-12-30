
from django.apps import AppConfig


class UserSetting(AppConfig):
    name = "bitlipa.apps.users"

    def ready(self):
        import bitlipa.apps.users.signals  # noqa
