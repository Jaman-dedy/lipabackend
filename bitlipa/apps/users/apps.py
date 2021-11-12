
from django.apps import AppConfig


class UserConfig(AppConfig):
    name = "bitlipa.apps.users"

    def ready(self):
        import bitlipa.apps.users.signals
