import json
import datetime
import time
import random
from django.conf import settings
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.db import models
from rest_framework import status

from bitlipa.resources import constants
from bitlipa.resources import error_messages
from bitlipa.utils.list_utils import filter_list
from bitlipa.utils.to_int import to_int
from bitlipa.utils.to_decimal import to_decimal
from bitlipa.utils.get_object_attr import get_object_attr
from bitlipa.utils.http_request import http_request
from bitlipa.utils.cybavo_checksum import CYBAVOChecksum
from bitlipa.apps.crypto_wallets.models import CryptoWallet


class TransactionManager(models.Manager):
    def list(self, user=None, **kwargs):
        table_fields = {}
        (page, per_page) = (to_int(kwargs.get('page'), 1), to_int(kwargs.get('per_page'), constants.DB_ITEMS_LIMIT))

        for key in filter_list(kwargs.keys(), values_to_exclude=['page', 'per_page']):
            if kwargs[key] is not None:
                table_fields[key] = kwargs[key]

        query = models.Q(**{'deleted_at': None, **table_fields})

        if not get_object_attr(user, "is_admin"):
            query = query & (models.Q(sender_id=user.id) | models.Q(receiver_id=user.id))

        object_list = self.model.objects.filter(query).order_by('-created_at')
        data = Paginator(object_list, per_page).page(page).object_list
        return {
            'data': data,
            'meta': {
                'page': page,
                'per_page': per_page,
                'total': object_list.count()
            }
        }

    def send_funds(self, user=None, **kwargs):
        (requests, errors) = ([], {})
        if not kwargs.get('wallet_id'):
            errors['wallet_id'] = error_messages.REQUIRED.format('wallet ID is ')

        if not kwargs.get('data') \
                or not isinstance(kwargs.get('data'), list)\
                or (isinstance(kwargs.get('data'), list) and not len(kwargs.get('data'))):
            errors['data'] = error_messages.REQUIRED.format('request data is ')

        if isinstance(kwargs.get('data'), list) and len(kwargs.get('data')):
            for data in kwargs.get('data'):
                if not data.get('address'):
                    errors['address'] = error_messages.REQUIRED.format('recipient address is ')
                if not data.get('amount'):
                    errors['amount'] = error_messages.REQUIRED.format('amount is ')

        if len(errors) != 0:
            raise ValidationError(str(errors))

        master_wallet = CryptoWallet.objects.get(
            wallet_id=kwargs.get('wallet_id'), type__iexact=str(self.model.Types.WITHDRAW.label), is_master=True)

        for data in kwargs.get('data'):
            requests.append({
                'order_id': f'{master_wallet.order_id_prefix}{random.randint(1, int(time.time()))}',
                'address': data.get('address'),
                'amount': data.get('amount'),
                'user_id': str(user.id),
                'memo': data.get('memo'),
                'message': data.get('message'),
                'block_average_fee': data.get('block_average_fee'),
                'manual_fee': data.get('manual_fee', data.get('fees'))
            })

        payload = json.dumps({'requests': requests})

        checksum = CYBAVOChecksum(secret=master_wallet.api_secret, payload=payload).build()
        response = http_request(
            url=f'{settings.THRESH0LD_API}/v1/sofa/wallets/{master_wallet.wallet_id}/sender/transactions?r={checksum.r}&t={checksum.t}',
            method='POST',
            data=payload,
            headers={'X-API-CODE': master_wallet.api_token, 'X-CHECKSUM': str(checksum), }
        )

        if not status.is_success(response.status_code):
            raise ValidationError(str(response.json()))

        return response.json()

    def create_or_update_transaction(self, **kwargs):
        tx_model = self.model
        tx_state = tx_model.get_transaction_state(kwargs.get('state')).get('label')
        tx_type = tx_model.get_transaction_type(kwargs.get('type')).get('label')
        tx_processing_state = tx_model.get_transaction_processing_state(kwargs.get('processing_state')).get('label')

        try:
            transaction = tx_model.objects.get(order_id=kwargs.get('order_id'), type__iexact=tx_type) if kwargs.get('order_id') \
                else tx_model.objects.get(transaction_id=kwargs.get('txid'), vout_index=kwargs.get('vout_index'), type__iexact=tx_type)
        except tx_model.DoesNotExist:
            transaction = tx_model()

        tx_fees = to_decimal(kwargs.get('fees', transaction.fees.amount)) * (1 / 10**to_decimal(kwargs.get('decimal'), 8))
        tx_amount = to_decimal(kwargs.get('amount', transaction.amount.amount)) * (1 / 10**to_decimal(kwargs.get('decimal'), 8))
        tx_total_amount = kwargs.get('total_amount', tx_amount + tx_fees)

        crypto_wallets = CryptoWallet.objects.filter(wallet_id=kwargs.get('wallet_id'),
                                                     address__in=[kwargs.get('from_address'), kwargs.get('to_address')])
        if len(crypto_wallets):
            for crypto_wallet in crypto_wallets:
                if tx_type == str(tx_model.Types.WITHDRAW.label) and crypto_wallet.address == kwargs.get('from_address'):
                    crypto_wallet.balance.amount -= tx_total_amount  # debit sender wallet

                if tx_type == str(tx_model.Types.DEPOSIT.label) and crypto_wallet.address == kwargs.get('to_address'):
                    crypto_wallet.balance.amount += tx_amount  # credit receiver wallet

            if not transaction.is_balance_updated and tx_processing_state == str(tx_model.ProcessingState.DONE.label)\
                and (tx_type == str(tx_model.Types.DEPOSIT.label)
                     or (tx_type == str(tx_model.Types.WITHDRAW.label) and tx_state == str(tx_model.State.IN_CHAIN.label))
                     ):
                CryptoWallet.objects.bulk_update(crypto_wallets, fields=['balance'])
                transaction.is_balance_updated = True

        transaction.type = tx_type
        transaction.wallet_id = kwargs.get('wallet_id', transaction.wallet_id)
        transaction.order_id = kwargs.get('order_id', transaction.order_id)
        transaction.serial = kwargs.get('serial', transaction.serial)
        transaction.vout_index = kwargs.get('vout_index', transaction.vout_index)
        transaction.transaction_id = kwargs.get('txid', kwargs.get('transaction_id', transaction.transaction_id))
        transaction.currency = kwargs.get("currency", constants.BTC)
        transaction.fees = tx_fees or 0
        transaction.amount = tx_amount or 0
        transaction.total_amount = tx_total_amount
        transaction.from_address = kwargs.get('from_address', transaction.from_address)
        transaction.to_address = kwargs.get('to_address', transaction.to_address)
        transaction.description = kwargs.get('description', transaction.description)
        transaction.state = tx_state

        transaction.save(using=self._db)
        return transaction

    def delete(self, id=None, user=None):
        transaction = self.model.objects.get(id=id) \
            if get_object_attr(user, "is_admin")\
            else self.model.objects.get(id=id, user_id=get_object_attr(user, "id"))

        transaction.deleted_at = datetime.datetime.now()
        transaction.save(using=self._db)
        return transaction
