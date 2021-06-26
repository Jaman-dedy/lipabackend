from django.db import models
from bitlipa.resources import error_messages
import datetime
from django.core.exceptions import ValidationError


class FiatWalletManager(models.Manager):
    def create_wallet(self, decoded_token, **kwargs):
        fiat_wallet = self.model()

        if not kwargs.get('wallet_name'):
            raise ValidationError(error_messages.REQUIRED.format('Wallet name is '))

        if not kwargs.get('wallet_currency'):
            raise ValidationError(error_messages.REQUIRED.format('Wallet currency is '))
        phonenumber = decoded_token.get('phonenumber')
        fiat_wallet.wallet_name = kwargs.get('wallet_name')
        fiat_wallet.wallet_number = f'{kwargs.get("wallet_currency")}-{phonenumber}'
        fiat_wallet.wallet_currency = kwargs.get('wallet_currency')

        fiat_wallet.save(using=self._db)
        return fiat_wallet

    def update(self, id=None, **kwargs):
        fiat_wallet = self.model.objects.get(id=id)

        fiat_wallet.wallet_name = kwargs.get('wallet_name') or fiat_wallet.wallet_name
        fiat_wallet.wallet_number = kwargs.get('wallet_number') or fiat_wallet.wallet_number
        fiat_wallet.wallet_currency = kwargs.get('wallet_currency') or fiat_wallet.wallet_currency

        fiat_wallet.save(using=self._db)
        return fiat_wallet

    def delete(self, id=None, **kwargs):
        fiat_wallet = self.model.objects.get(id=id)

        fiat_wallet.deleted_at = datetime.datetime.now()

        fiat_wallet.save(using=self._db)
        return fiat_wallet
