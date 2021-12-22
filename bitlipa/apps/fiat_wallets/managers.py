from django.db import models
from bitlipa.resources import error_messages
import datetime
from django.core.exceptions import ValidationError


class FiatWalletManager(models.Manager):
    def create_wallet(self, user, **kwargs):
        fiat_wallet = self.model()

        if not kwargs.get('name'):
            raise ValidationError(error_messages.REQUIRED.format('Wallet name is '))

        if not kwargs.get('currency'):
            raise ValidationError(error_messages.REQUIRED.format('Wallet currency is '))
        fiat_wallet.name = kwargs.get('name')
        fiat_wallet.number = f'{user.phonenumber}-{kwargs.get("currency")}'
        fiat_wallet.currency = kwargs.get('currency')
        fiat_wallet.user = user

        fiat_wallet.save(using=self._db)
        return fiat_wallet

    def update(self, id=None, **kwargs):
        fiat_wallet = self.model.objects.get(id=id)

        fiat_wallet.name = kwargs.get('name') or fiat_wallet.name
        fiat_wallet.currency = kwargs.get('currency') or fiat_wallet.currency
        fiat_wallet.currency = kwargs.get('currency') or fiat_wallet.currency

        fiat_wallet.save(using=self._db)
        return fiat_wallet

    def delete(self, id=None, **kwargs):
        fiat_wallet = self.model.objects.get(id=id)

        fiat_wallet.deleted_at = datetime.datetime.now()

        fiat_wallet.save(using=self._db)
        return fiat_wallet
