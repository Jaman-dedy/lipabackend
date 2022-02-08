from django.apps import AppConfig


class TransactionConfig(AppConfig):
    name = 'bitlipa.apps.transactions'

    def ready(self):
        from . import signals  # noqa
