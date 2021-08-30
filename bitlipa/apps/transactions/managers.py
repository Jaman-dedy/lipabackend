import json
import datetime
import time
import random
import uuid
from django.conf import settings
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.db import models
from rest_framework import status
from django.db.utils import IntegrityError

from bitlipa.resources import constants
from bitlipa.resources import error_messages
from bitlipa.utils.to_int import to_int
from bitlipa.utils.to_decimal import to_decimal
from bitlipa.utils.get_object_attr import get_object_attr
from bitlipa.utils.http_request import http_request
from bitlipa.utils.is_valid_uuid import is_valid_uuid
from bitlipa.utils.remove_dict_none_values import remove_dict_none_values
from bitlipa.utils.cybavo_checksum import CYBAVOChecksum
from bitlipa.apps.crypto_wallets.models import CryptoWallet
from bitlipa.apps.fiat_wallet.models import FiatWallet
from bitlipa.apps.fees.models import Fee
from bitlipa.apps.currency_exchange.models import CurrencyExchange


class TransactionManager(models.Manager):
    def list(self, user=None, **kwargs):
        table_fields = {**kwargs}
        page = to_int(kwargs.get('page'), 1)
        per_page = to_int(kwargs.get('per_page'), constants.DB_ITEMS_LIMIT)

        for key in ['page', 'per_page']:
            table_fields.pop(key, None)  # remove fields not in the DB table

        query = models.Q(**{'deleted_at': None, **remove_dict_none_values(table_fields)})

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

    def send_funds(self, **kwargs):
        transaction = self.model()

        errors = {
            'source_wallet': error_messages.REQUIRED.format('source wallet is ') if not kwargs.get('source_wallet') else None,
            'target_wallet': error_messages.REQUIRED.format('target wallet is ') if not kwargs.get('target_wallet') else None,
            'amount': error_messages.REQUIRED.format('amount is ') if not kwargs.get('amount') else None
        }

        if len(remove_dict_none_values(errors)) != 0:
            raise ValidationError(str(errors))

        try:
            source_wallet = CryptoWallet.objects.get(
                models.Q(**{'id' if is_valid_uuid(kwargs.get('source_wallet')) else 'address': kwargs.get('source_wallet')}))
        except CryptoWallet.DoesNotExist:
            source_wallet = FiatWallet.objects.get(
                models.Q(**{'id' if is_valid_uuid(kwargs.get('source_wallet')) else 'number': kwargs.get('source_wallet')}))
        try:
            target_wallet = CryptoWallet.objects.get(
                models.Q(**{'id' if is_valid_uuid(kwargs.get('target_wallet')) else 'address': kwargs.get('target_wallet')}))
        except CryptoWallet.DoesNotExist:
            target_wallet = FiatWallet.objects.get(
                models.Q(**{'id' if is_valid_uuid(kwargs.get('target_wallet')) else 'number': kwargs.get('target_wallet')}))

        tx_fee = Fee.objects.get_fee(name__iexact="internal funds transfer")
        fx_fee = 0
        tx_amount = to_decimal(kwargs.get('amount'))
        tx_total_amount = tx_amount + tx_fee.amount

        errors['amount'] = error_messages.INVALID_AMOUNT if tx_amount <= 0 else None
        errors['source_wallet'] = error_messages.INSUFFICIENT_FUNDS if source_wallet.balance.amount - tx_total_amount <= 0 else None
        errors['target_wallet'] = error_messages.SAME_SOURCE_TARGET_WALLET if source_wallet.id == target_wallet.id else None

        if len(remove_dict_none_values(errors)) != 0:
            raise ValidationError(str(errors))

        # debit sender wallet
        source_wallet.balance.amount -= tx_total_amount

        # credit receiver wallet
        if source_wallet.currency == target_wallet.currency:
            target_wallet.balance.amount += tx_amount
        else:
            currency_exchange = CurrencyExchange.objects.convert(**{
                'amount': tx_amount,
                'base_currency': source_wallet.currency,
                'currency': target_wallet.currency
            })
            fx_fee = currency_exchange.get('fee')
            tx_amount = to_decimal(currency_exchange.get('amount'))
            target_wallet.balance.amount += to_decimal(currency_exchange.get('amount'))

        transaction.type = constants.INTERNAL_USERS_TRANSACTION
        # transaction.wallet_id = kwargs.get('wallet_id')
        # transaction.order_id = kwargs.get('order_id')
        # transaction.serial = kwargs.get('serial')
        transaction.transaction_id = uuid.uuid4().hex
        transaction.from_currency = source_wallet.currency
        transaction.to_currency = target_wallet.currency
        transaction.fee = tx_fee.amount or 0
        transaction.fx_fee = fx_fee or 0
        transaction.amount = tx_amount or 0
        transaction.total_amount = tx_total_amount
        transaction.from_address = get_object_attr(source_wallet, 'address', get_object_attr(source_wallet, 'number'))
        transaction.to_address = get_object_attr(target_wallet, 'address', get_object_attr(target_wallet, 'number'))
        transaction.description = kwargs.get('description')
        transaction.state = self.model.ProcessingState.DONE.label
        transaction.sender = source_wallet.user
        transaction.receiver = target_wallet.user

        if kwargs.get('send') is True:
            source_wallet.save()
            target_wallet.save()
            transaction.save(using=self._db)

        return transaction

    def topup_funds(self, user=None, **kwargs):
        errors = {
            'phonenumber': error_messages.REQUIRED.format('phonenumber is ') if not kwargs.get('phonenumber') else None,
            'amount': error_messages.REQUIRED.format('amount is ') if not kwargs.get('amount') else None,
            'currency': error_messages.REQUIRED.format('currency is ') if not kwargs.get('currency') else None,
            'description': error_messages.REQUIRED.format('description is ') if not kwargs.get('description') else None,
            'callback_url': error_messages.REQUIRED.format('callback_url is ') if not kwargs.get('callback_url') else None,
            'metadata': error_messages.REQUIRED.format('metadata is ') if not kwargs.get('metadata') else None

        }

        if len(remove_dict_none_values(errors)) != 0:
            raise ValidationError(str(errors))

        payload = {
            'phonenumber': kwargs.get('phonenumber'),
            'amount': kwargs.get('amount'),
            'currency': kwargs.get('currency'),
            'description': kwargs.get('description'),
            'callback_url': kwargs.get('callback_url'),
            'metadata': kwargs.get('metadata', {}),
            'send_instructions': kwargs.get('send_instructions')
        }

        payload = json.dumps(payload)

        response = http_request(
            url=f'{settings.BEYONIC_API}/collectionrequests',
            method='POST',
            data=payload,
            headers={
                'Authorization': f'Token {settings.BEYONIC_API_TOKEN}',
                'Content-Type': 'application/json'
            }
        )

        if not status.is_success(response.status_code):
            raise ValidationError(str(response.json()))

        return response.json()

    def beyonic_withdraw(self, **kwargs):
        errors = {
            'phonenumber': error_messages.REQUIRED.format('phonenumber is ') if not kwargs.get('phonenumber') else None,
            'amount': error_messages.REQUIRED.format('amount is ') if not kwargs.get('amount') else None,
            'currency': error_messages.REQUIRED.format('currency is ') if not kwargs.get('currency') else None,
            'description': error_messages.REQUIRED.format('description is ') if not kwargs.get('description') else None,
            'callback_url': error_messages.REQUIRED.format('callback_url is ') if not kwargs.get('callback_url') else None,
            'first_name': error_messages.REQUIRED.format('first_name is ') if not kwargs.get('first_name') else None,
            'last_name': error_messages.REQUIRED.format('last_name is ') if not kwargs.get('last_name') else None,
            'payment_type': error_messages.REQUIRED.format('payment_type is ') if not kwargs.get('payment_type') else None,
            'metadata': error_messages.REQUIRED.format('metadata is ') if not kwargs.get('metadata') else None
        }

        if len(remove_dict_none_values(errors)) != 0:
            raise ValidationError(str(errors))

        payload = {
            'phonenumber': kwargs.get('phonenumber'),
            'amount': kwargs.get('amount'),
            'currency': kwargs.get('currency'),
            'description': kwargs.get('description'),
            'callback_url': kwargs.get('callback_url'),
            'first_name': kwargs.get('first_name'),
            'last_name': kwargs.get('last_name'),
            'payment_type': kwargs.get('payment_type'),
            'send_instructions': kwargs.get('send_instructions')
        }

        payload = json.dumps(payload)
        response = http_request(
            url=f'{settings.BEYONIC_API}/payments',
            method='POST',
            data=payload,
            headers={
                'Authorization': f'Token {settings.BEYONIC_API_TOKEN}',
                'Content-Type': 'application/json'
            }
        )

        if not status.is_success(response.status_code):
            raise ValidationError(str(response.json()))
        return response.json()

    def create_or_update_topup_transaction(self, **kwargs):
        tx_model = self.model
        errors = {
            'data' : error_messages.REQUIRED.format('data is ') if not kwargs.get('data') else None,
            'event' : error_messages.REQUIRED.format('event is ') if not kwargs.get('event') else None,
        }

        data = kwargs.get('data')

        errors['metadata'] = error_messages.REQUIRED.format('metadata is ') if not data.get('metadata') else None
        errors['id'] = error_messages.REQUIRED.format('id is ') if not data.get('id') else None

        metadata = data.get('metadata')

        if not metadata.get('crypto_wallet_id') and not metadata.get('fiat_wallet_id') :
            errors['wallet_id'] = error_messages.REQUIRED.format('wallet_id is ')

        if len(remove_dict_none_values(errors)) != 0:
            raise ValidationError(str(errors))

        tx_crypto_wallet_id = metadata.get("crypto_wallet_id")
        tx_fiat_wallet_id = metadata.get("fiat_wallet_id")
        tx_id = data.get('id')
        tx_fee = to_decimal(data.get('fee', 0))
        tx_amount = to_decimal(data.get('amount'))
        tx_total_amount = data.get('total_amount', tx_amount + tx_fee)

        try:
            transaction = tx_model.objects.get(transaction_id=tx_id, serial=kwargs.get('event'))
            if transaction:
                raise IntegrityError(f'this transaction {tx_id}')

        except tx_model.DoesNotExist:
            transaction = tx_model()

        user_wallet = CryptoWallet.objects.get(id=tx_crypto_wallet_id) if tx_crypto_wallet_id \
            else FiatWallet.objects.get(id=tx_fiat_wallet_id)

        transaction.transaction_id = tx_id
        transaction.serial = kwargs.get('event')
        transaction.type = constants.BEYONIC_TOP_UP
        transaction.wallet_id = get_object_attr(user_wallet, 'wallet_id')
        transaction.currency = user_wallet.currency
        transaction.description = kwargs.get('description')
        transaction.state = data.get('status')
        transaction.fee = tx_fee or 0
        transaction.amount = tx_amount or 0
        transaction.total_amount = tx_total_amount
        transaction.from_address = data.get('phone_number')
        transaction.to_address = get_object_attr(user_wallet, 'address') or\
            get_object_attr(user_wallet, 'number')
        transaction.receiver = user_wallet.user

        if(data.get("status") == "success" or data.get("status") == "successful"):
            # TODO : Convert fiat amount to crypto
            user_wallet.balance.amount += tx_amount
            user_wallet.save()
            transaction.save(using=self._db)
        return transaction

    def send_crypto_funds(self, user=None, **kwargs):
        (requests, errors) = ([], {})
        if not kwargs.get('wallet_id'):
            errors['wallet_id'] = error_messages.REQUIRED.format('wallet ID is ')

        if not kwargs.get('data') \
                or not isinstance(kwargs.get('data'), list)\
                or (isinstance(kwargs.get('data'), list) and not len(kwargs.get('data'))):
            errors['data'] = error_messages.REQUIRED.format('request data is ')

        if isinstance(kwargs.get('data'), list) and len(kwargs.get('data')):
            for data in kwargs.get('data'):
                errors['address'] = error_messages.REQUIRED.format('recipient address is ') if not data.get('address') else None
                errors['amount'] = error_messages.REQUIRED.format('amount is ') if not data.get('amount') else None

        if len(remove_dict_none_values(errors)) != 0:
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
                'manual_fee': data.get('manual_fee', data.get('fee'))
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

    def create_or_update_crypto_transaction(self, **kwargs):
        tx_model = self.model
        tx_state = tx_model.get_transaction_state(kwargs.get('state')).get('label')
        tx_type = tx_model.get_transaction_type(kwargs.get('type')).get('label')
        tx_processing_state = tx_model.get_transaction_processing_state(kwargs.get('processing_state')).get('label')

        try:
            transaction = tx_model.objects.get(order_id=kwargs.get('order_id'), type__iexact=tx_type) if kwargs.get('order_id') \
                else tx_model.objects.get(transaction_id=kwargs.get('txid'), vout_index=kwargs.get('vout_index'), type__iexact=tx_type)
        except tx_model.DoesNotExist:
            transaction = tx_model()

        tx_fee = to_decimal(kwargs.get('fee', transaction.fee.amount)) * (1 / 10**to_decimal(kwargs.get('decimal'), 8))
        tx_amount = to_decimal(kwargs.get('amount', transaction.amount.amount)) * (1 / 10**to_decimal(kwargs.get('decimal'), 8))
        tx_total_amount = kwargs.get('total_amount', tx_amount + tx_fee)

        crypto_wallets = CryptoWallet.objects.filter(wallet_id=kwargs.get('wallet_id'),
                                                     address__in=[kwargs.get('from_address'), kwargs.get('to_address')])
        if len(crypto_wallets):
            for crypto_wallet in crypto_wallets:
                transaction.sender = get_object_attr(crypto_wallet, "user") if crypto_wallet.address == kwargs.get('from_address') else None
                transaction.receiver = get_object_attr(crypto_wallet, "user") if crypto_wallet.address == kwargs.get('to_address') else None
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
        transaction.fee = tx_fee or 0
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
