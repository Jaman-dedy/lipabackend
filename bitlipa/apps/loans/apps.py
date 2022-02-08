from django.apps import AppConfig


class LoanConfig(AppConfig):
    name = 'bitlipa.apps.loans'

    def ready(self):
        from . import signals  # noqa
