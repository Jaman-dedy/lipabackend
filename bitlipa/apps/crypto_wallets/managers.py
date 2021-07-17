from django.core.paginator import Paginator
from django.db import models
import datetime
from django.core.exceptions import ValidationError


from bitlipa.resources import error_messages
from bitlipa.resources import constants
from bitlipa.utils.to_int import to_int
from bitlipa.utils.get_object_attr import get_object_attr


class CryptoWalletManager(models.Manager):
    def get_all(self, page=1, per_page=constants.DB_ITEMS_LIMIT, **kwargs):
        object_list = self.model.objects.filter(**{'deleted_at': None, **kwargs}).order_by('-created_at')
        return {
            'data': Paginator(object_list, to_int(per_page, constants.DB_ITEMS_LIMIT)).page(to_int(page, 1)).object_list,
            'meta': {
                'page': to_int(page, 1),
                'per_page': to_int(per_page, constants.DB_ITEMS_LIMIT),
                'total': object_list.count()
            }
        }

    def create_wallet(self, user, **kwargs):
        crypto_wallet = self.model()
        errors = {}
        if not kwargs.get('name'):
            errors['name'] = error_messages.REQUIRED.format('wallet name is ')
        if not kwargs.get('currency'):
            errors['currency'] = error_messages.REQUIRED.format('wallet currency is ')
        if not kwargs.get('address'):
            errors['address'] = error_messages.REQUIRED.format('wallet address is ')
        if len(errors) != 0:
            raise ValidationError(str(errors))

        crypto_wallet.user = user if get_object_attr(user, "id") else None
        crypto_wallet.name = kwargs.get('name')
        crypto_wallet.type = kwargs.get("type")
        crypto_wallet.wallet_id = kwargs.get("wallet_id")
        crypto_wallet.currency = kwargs.get("currency") or constants.BTC
        crypto_wallet.balance = kwargs.get('balance') or 0
        crypto_wallet.address = kwargs.get('address')
        crypto_wallet.description = kwargs.get('description')
        crypto_wallet.api_token = kwargs.get('api_token')
        crypto_wallet.api_secret = kwargs.get('api_secret')
        crypto_wallet.api_refresh_token = kwargs.get('api_refresh_token')
        crypto_wallet.logo_url = kwargs.get('logo_url')

        if get_object_attr(user, "is_admin", False):
            crypto_wallet.is_master = kwargs.get('is_master')

        crypto_wallet.save(using=self._db)
        return crypto_wallet

    def update(self, id=None, user=None, **kwargs):
        crypto_wallet = self.model.objects.get(id=id, user_id=user.id) \
            if get_object_attr(user, "id")\
            else self.model.objects.get(id=id)

        crypto_wallet.name = kwargs.get('name') or crypto_wallet.name
        crypto_wallet.type = kwargs.get("type") or crypto_wallet.type
        crypto_wallet.wallet_id = kwargs.get("wallet_id") or crypto_wallet.wallet_id
        crypto_wallet.currency = kwargs.get("currency") or crypto_wallet.currency
        crypto_wallet.balance = crypto_wallet.balance if kwargs.get('balance') is None else kwargs.get('balance')
        crypto_wallet.address = kwargs.get('address') or crypto_wallet.address
        crypto_wallet.description = crypto_wallet.description if kwargs.get('description') is None else kwargs.get('description')
        crypto_wallet.api_token = crypto_wallet.api_token if kwargs.get('api_token') is None else kwargs.get('api_token')
        crypto_wallet.api_secret = crypto_wallet.api_secret if kwargs.get('api_secret') is None else kwargs.get('api_secret')
        crypto_wallet.api_refresh_token = crypto_wallet.api_refresh_token if kwargs.get('api_refresh_token') is None \
            else kwargs.get('api_refresh_token')
        crypto_wallet.logo_url = crypto_wallet.api_secret if kwargs.get('logo_url') is None else kwargs.get('logo_url')

        if get_object_attr(user, "is_admin", False):
            crypto_wallet.is_master = kwargs.get('is_master') or crypto_wallet.is_master

        crypto_wallet.save(using=self._db)
        return crypto_wallet

    def delete(self, id=None, user=None):
        crypto_wallet = self.model.objects.get(id=id, user_id=user.id) \
            if get_object_attr(user, "id")\
            else self.model.objects.get(id=id)

        crypto_wallet.deleted_at = datetime.datetime.now()
        crypto_wallet.save(using=self._db)
        return crypto_wallet
