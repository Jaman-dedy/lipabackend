import json
import datetime
from contextlib import suppress
from django.conf import settings
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.db import models
from rest_framework import status


from bitlipa.resources import constants
from bitlipa.resources import error_messages
from bitlipa.utils.list_utils import filter_list
from bitlipa.utils.to_int import to_int
from bitlipa.utils.get_object_attr import get_object_attr
from bitlipa.utils.http_request import http_request
from bitlipa.utils.cybavo_checksum import CYBAVOChecksum


class CryptoWalletManager(models.Manager):
    def list(self, user=None, **kwargs):

        table_fields = {}
        (page, per_page) = (to_int(kwargs.get('page'), 1), to_int(kwargs.get('per_page'), constants.DB_ITEMS_LIMIT))

        if 'is_master' in kwargs and kwargs.get('all'):
            kwargs.pop('is_master')

        for key in filter_list(kwargs.keys(), values_to_exclude=['all', 'page', 'per_page']):
            if kwargs[key] is not None:
                table_fields[key] = kwargs[key]

        table_fields['user_id'] = user.id

        if get_object_attr(user, "is_admin") and kwargs.get('all'):
            table_fields.pop('user_id')

        object_list = self.model.objects.filter(**{'deleted_at': None, **table_fields}).order_by('-created_at')
        return {
            'data': Paginator(object_list, per_page).page(page).object_list,
            'meta': {
                'page': page,
                'per_page': per_page,
                'total': object_list.count()
            }
        }

    def create_wallet(self, user, **kwargs):
        (crypto_wallet, errors) = (self.model(), {})
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
        crypto_wallet.order_id_prefix = kwargs.get("order_id_prefix")
        crypto_wallet.currency = kwargs.get("currency", constants.BTC)
        crypto_wallet.balance = kwargs.get('balance', 0)
        crypto_wallet.address = kwargs.get('address')
        crypto_wallet.description = kwargs.get('description')
        crypto_wallet.api_token = kwargs.get('api_token')
        crypto_wallet.api_secret = kwargs.get('api_secret')
        crypto_wallet.api_refresh_token = kwargs.get('api_refresh_token')
        crypto_wallet.logo_url = kwargs.get('logo_url')

        if get_object_attr(user, "is_admin"):
            crypto_wallet.is_master = kwargs.get('is_master')

        crypto_wallet.save(using=self._db)
        return crypto_wallet

    def update(self, id=None, user=None, **kwargs):
        crypto_wallet = self.model.objects.get(id=id) \
            if get_object_attr(user, "is_admin")\
            else self.model.objects.get(id=id, user_id=get_object_attr(user, "id"))

        crypto_wallet.name = kwargs.get('name', crypto_wallet.name)
        crypto_wallet.type = kwargs.get("type", crypto_wallet.type)
        crypto_wallet.wallet_id = kwargs.get("wallet_id", crypto_wallet.wallet_id)
        crypto_wallet.order_id_prefix = kwargs.get("order_id_prefix", crypto_wallet.order_id_prefix)
        crypto_wallet.currency = kwargs.get("currency", crypto_wallet.currency)
        crypto_wallet.balance = kwargs.get('balance', crypto_wallet.balance)
        crypto_wallet.address = kwargs.get('address', crypto_wallet.address)
        crypto_wallet.description = kwargs.get('description', crypto_wallet.description)
        crypto_wallet.api_token = kwargs.get('api_token', crypto_wallet.api_token)
        crypto_wallet.api_secret = kwargs.get('api_secret', crypto_wallet.api_secret)
        crypto_wallet.api_refresh_token = kwargs.get('api_refresh_token', crypto_wallet.api_refresh_token)
        crypto_wallet.logo_url = kwargs.get('logo_url', crypto_wallet.logo_url)

        if get_object_attr(user, "is_admin"):
            crypto_wallet.is_master = kwargs.get('is_master', crypto_wallet.is_master)

        crypto_wallet.save(using=self._db)
        return crypto_wallet

    def create_wallet_address(self, user=None, **kwargs):
        if not kwargs.get('wallet_id'):
            raise ValidationError(error_messages.REQUIRED.format('wallet ID is '))

        (count, master_wallet) = (1, self.model.objects.get(wallet_id=kwargs.get('wallet_id'), is_master=True))

        with suppress(Exception):
            count = len(kwargs.get('data'))

        payload = json.dumps({"count": count, "memos": kwargs.get('memos')})
        checksum = CYBAVOChecksum(secret=master_wallet.api_secret, payload=payload).build()
        response = http_request(
            url=f'{settings.THRESH0LD_API}/v1/sofa/wallets/{master_wallet.wallet_id}/addresses?r={checksum.r}&t={checksum.t}',
            method='POST',
            data=payload,
            headers={'X-API-CODE': master_wallet.api_token, 'X-CHECKSUM': str(checksum), }
        )

        if not status.is_success(response.status_code):
            raise ValidationError(str(response.json()))

        wallets_list = []
        for (index, address) in enumerate(response.json().get('addresses')):
            wallet_to_create = next(iter(kwargs.get('data', [])[index:]), {'name': master_wallet.currency})
            crypto_wallet = self.model()
            crypto_wallet.user = user if get_object_attr(user, "id") else None
            crypto_wallet.name = wallet_to_create.get('name')
            crypto_wallet.type = master_wallet.type
            crypto_wallet.wallet_id = master_wallet.wallet_id
            crypto_wallet.order_id_prefix = master_wallet.order_id_prefix
            crypto_wallet.currency = master_wallet.currency
            crypto_wallet.balance = 0
            crypto_wallet.address = address
            crypto_wallet.description = wallet_to_create.get('description')
            crypto_wallet.logo_url = master_wallet.logo_url
            wallets_list.append(crypto_wallet)
        return self.model.objects.bulk_create(wallets_list)

    def list_wallet_addresses(self, user=None, wallet_id=None, **kwargs):
        if not (wallet_id or kwargs.get('wallet_id')):
            raise ValidationError(error_messages.REQUIRED.format('wallet ID is '))

        master_wallet = self.model.objects.get(wallet_id=wallet_id or kwargs.get('wallet_id'), is_master=True)
        checksum = CYBAVOChecksum(secret=master_wallet.api_secret).build()

        response = http_request(
            url=f'{settings.THRESH0LD_API}/v1/sofa/wallets/{master_wallet.wallet_id}/addresses?r={checksum.r}&t={checksum.t}',
            method='GET',
            headers={'X-API-CODE': master_wallet.api_token, 'X-CHECKSUM': str(checksum), }
        )

        if not status.is_success(response.status_code):
            raise ValidationError(str(response.json()))

        return {
            'status_code': response.status_code,
            'data': {
                'user_id': master_wallet.user_id,
                'name': master_wallet.name,
                'type': master_wallet.type,
                'wallet_id': master_wallet.wallet_id,
                'order_id_prefix': master_wallet.order_id_prefix,
                'currency': master_wallet.currency,
                'balance': format(master_wallet.balance.amount, '.18f'),
                'address': master_wallet.address,
                'description': master_wallet.description,
                'logo_url': master_wallet.logo_url,
                'addresses': response.json().get('wallet_address')}
        }

    def delete(self, id=None, user=None):
        crypto_wallet = self.model.objects.get(id=id) \
            if get_object_attr(user, "is_admin")\
            else self.model.objects.get(id=id, user_id=get_object_attr(user, "id"))

        crypto_wallet.deleted_at = datetime.datetime.now()
        crypto_wallet.save(using=self._db)
        return crypto_wallet
