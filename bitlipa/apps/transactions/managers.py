import json
import datetime
import dateutil.relativedelta
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
from bitlipa.apps.fiat_wallets.models import FiatWallet
from bitlipa.apps.currency_exchange.models import CurrencyExchange
from bitlipa.utils.get_m_pesa_token import create_token
from bitlipa.apps.mpesa_auth.models import MpesaAuth
from bitlipa.utils.m_pesa_http import m_pesa_http
from bitlipa.resources.error_messages import M_PESA_TOKEN_EXPIRED
from bitlipa.apps.transactions.helper.top_up_failed import topup_failed
from bitlipa.apps.transactions.helper.top_up_success import topup_success
from .helpers import calculate_fees , check_transaction_limits


class TransactionManager(models.Manager):
    def list(self, user=None, **kwargs):
        table_fields = {**kwargs}
        page = to_int(kwargs.get('page'), 1)
        per_page = to_int(kwargs.get('per_page'), constants.DB_ITEMS_LIMIT)

        for key in ['page', 'per_page', 'user_id']:
            table_fields.pop(key, None)  # remove fields not in the DB table

        if table_fields.get('source_address') and table_fields.get('source_address') == table_fields.get('target_address'):
            query = models.Q(source_address__iexact=kwargs.get('source_address')) | \
                models.Q(target_address__iexact=kwargs.get('target_address'))
            table_fields.pop('source_address', None)
            table_fields.pop('target_address', None)
            query = query & models.Q(
                **{'deleted_at': None, **remove_dict_none_values(table_fields)})
        else:
            query = models.Q(
                **{'deleted_at': None, **remove_dict_none_values(table_fields)})

        if get_object_attr(user, "is_admin") and is_valid_uuid(kwargs.get('user_id')):
            query = query & (models.Q(sender_id=kwargs.get('user_id')) | models.Q(
                receiver_id=kwargs.get('user_id')))

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

    def list_last_receivers(self, user=None, **kwargs):
        table_fields = {**kwargs}
        page = to_int(kwargs.get('page'), 1)
        per_page = to_int(kwargs.get('per_page'), constants.DB_ITEMS_LIMIT)

        for key in ['page', 'per_page']:
            table_fields.pop(key, None)  # remove fields not in the DB table

        query = models.Q(**{'deleted_at': None, 'receiver__isnull': False,
                         **remove_dict_none_values(table_fields)})
        query = query & models.Q(sender_id=user.id)
        query = query & (models.Q(sender_id=user.id) & ~
                         models.Q(receiver_id=user.id))

        object_list = self.model.objects.filter(query).distinct(
            'receiver_id').order_by('-receiver_id')

        data = Paginator(object_list, per_page).page(page).object_list
        return {
            'data': data,
            'meta': {
                'page': page,
                'per_page': per_page,
                'total': object_list.count()
            }
        }

    def send_funds(self, user, **kwargs):
        (transaction, errors) = (self.model(), {})
        (tx_fee, fx_fee, fx_rate) = (0, 0, 0)

        errors['source_wallet'] = error_messages.REQUIRED.format('source wallet is ') if not kwargs.get('source_wallet') else None
        errors['target_wallet'] = error_messages.REQUIRED.format('target wallet is ') if not kwargs.get('target_wallet') else None
        errors['amount'] = error_messages.REQUIRED.format('amount is ') if not kwargs.get('amount') else None

        if len(remove_dict_none_values(errors)) != 0:
            raise ValidationError(str(errors))

        try:
            source_wallet = CryptoWallet.objects.get(
                models.Q(**{'user_id': get_object_attr(user, 'id'),
                            'id' if is_valid_uuid(kwargs.get('source_wallet')) else 'address': kwargs.get('source_wallet')}))
        except CryptoWallet.DoesNotExist:
            source_wallet = FiatWallet.objects.get(
                models.Q(**{'user_id': get_object_attr(user, 'id'),
                            'id' if is_valid_uuid(kwargs.get('source_wallet')) else 'number': kwargs.get('source_wallet')}))
        try:
            target_wallet = CryptoWallet.objects.get(
                models.Q(**{'id' if is_valid_uuid(kwargs.get('target_wallet')) else 'address': kwargs.get('target_wallet')}))
        except CryptoWallet.DoesNotExist:
            target_wallet = FiatWallet.objects.get(
                models.Q(**{'id' if is_valid_uuid(kwargs.get('target_wallet')) else 'number': kwargs.get('target_wallet')}))

        if get_object_attr(source_wallet, 'type') != FiatWallet.Types.LOAN:
            tx_fee, fx_fee = calculate_fees(source_wallet, target_wallet, to_decimal(kwargs.get('amount')))

        tx_source_amount = to_decimal(kwargs.get('amount'))
        tx_source_total_amount = tx_source_amount + tx_fee + fx_fee
        tx_target_amount = tx_source_amount

        errors['amount'] = error_messages.INVALID_AMOUNT if tx_source_amount <= 0 else None
        errors['source_wallet'] = error_messages.INSUFFICIENT_FUNDS if source_wallet.balance.amount - tx_source_total_amount <= 0 else None
        errors['target_wallet'] = error_messages.SAME_SOURCE_TARGET_WALLET if source_wallet.id == target_wallet.id else None
        errors['limit'] = check_transaction_limits(user, tx_source_total_amount) or None

        if len(remove_dict_none_values(errors)) != 0:
            raise ValidationError(str(errors))

        # debit sender's wallet
        source_wallet.balance.amount -= tx_source_total_amount
        # credit receiver's wallet
        if source_wallet.currency == target_wallet.currency:
            target_wallet.balance.amount += to_decimal(tx_source_amount)
        else:
            currency_exchange = CurrencyExchange.objects.convert(**{
                'amount': tx_source_amount,
                'base_currency': source_wallet.currency,
                'currency': target_wallet.currency,
            })
            fx_rate = to_decimal(currency_exchange.get('rate'))
            tx_target_amount = to_decimal(currency_exchange.get('total_amount'))
            target_wallet.balance.amount += to_decimal(currency_exchange.get('total_amount'))

        transaction.type = constants.INTERNAL_USERS_TRANSACTION
        # transaction.wallet_id = kwargs.get('wallet_id')
        # transaction.order_id = kwargs.get('order_id')
        # transaction.serial = kwargs.get('serial')
        transaction.transaction_id = uuid.uuid4().hex
        transaction.source_currency = source_wallet.currency
        transaction.target_currency = target_wallet.currency
        transaction.fee = tx_fee
        transaction.fx_fee = fx_fee
        transaction.fx_rate = fx_rate
        transaction.source_amount = tx_source_amount
        transaction.source_total_amount = tx_source_total_amount
        transaction.target_amount = tx_target_amount
        transaction.source_address = get_object_attr(
            source_wallet, 'address', get_object_attr(source_wallet, 'number'))
        transaction.target_address = get_object_attr(
            target_wallet, 'address', get_object_attr(target_wallet, 'number'))
        transaction.description = kwargs.get('description')
        transaction.state = self.model.ProcessingState.DONE.label
        transaction.sender = source_wallet.user
        transaction.receiver = target_wallet.user

        if kwargs.get('send') is True:
            user.daily_tx_total_amount += tx_source_total_amount
            user.weekly_tx_total_amount += tx_source_total_amount
            user.monthly_tx_total_amount += tx_source_total_amount
            user.save()
            source_wallet.save()
            target_wallet.save()
            transaction.save(using=self._db)

        return transaction

    def topup_funds(self, user=None, **kwargs):
        REQUIRED_ERROR = error_messages.REQUIRED
        errors = {
            'PartyB': REQUIRED_ERROR.format('PartyB is ') if not kwargs.get('PartyB') else None,
            'BusinessShortCode': REQUIRED_ERROR.format('BusinessShortCode is ') if not kwargs.get('BusinessShortCode') else None,
            'PhoneNumber': REQUIRED_ERROR.format('PhoneNumber is ') if not kwargs.get('PhoneNumber') else None,
            'Amount': REQUIRED_ERROR.format('amount is ') if not kwargs.get('Amount') else None,
            'CallBackURL': REQUIRED_ERROR.format('CallBackURL is ') if not kwargs.get('CallBackURL') else None,
            'metadata': REQUIRED_ERROR.format('metadata is ') if not kwargs.get('metadata') else None
        }
        metadata = kwargs.get('metadata') if isinstance(
            kwargs.get('metadata'), dict) else {}
        errors['tx_fee'] = REQUIRED_ERROR.format(
            'fee is ') if metadata.get('tx_fee') is None else None
        errors['fx_fee'] = REQUIRED_ERROR.format(
            'fx fee is ') if metadata.get('fx_fee') is None else None
        errors['fx_rate'] = REQUIRED_ERROR.format(
            'fx rate is ') if metadata.get('fx_rate') is None else None
        errors['source_amount'] = REQUIRED_ERROR.format(
            'source amount is ') if metadata.get('source_amount') is None else None
        errors['source_total_amount'] = REQUIRED_ERROR.format(
            'source total amount is ') if metadata.get('source_total_amount') is None else None
        errors['target_amount'] = REQUIRED_ERROR.format(
            'target amount is ') if metadata.get('target_amount') is None else None

        if len(remove_dict_none_values(errors)) != 0:
            raise ValidationError(str(errors))

        payload = {
            'BusinessShortCode': kwargs.get('BusinessShortCode'),
            'Timestamp': kwargs.get('Timestamp'),
            'Amount': metadata.get('source_total_amount'),
            'Password': kwargs.get('Password'),
            'PartyA': kwargs.get('PartyA'),
            'PartyB': kwargs.get('PartyB'),
            'PhoneNumber': kwargs.get('PhoneNumber'),
            'TransactionDesc': kwargs.get('TransactionDesc'),
            'AccountReference': kwargs.get('AccountReference'),
            'CallBackURL': kwargs.get('CallBackURL'),
            'TransactionType': kwargs.get('TransactionType'),
            'metadata': metadata
        }

        payload = json.dumps(payload)
        access_token = MpesaAuth.objects.filter()
        if not access_token:
            create_token()
            access_token = access_token[0].access_token
        url = '/mpesa/stkpush/v1/processrequest'
        method = "POST"
        response = m_pesa_http(url, method, payload,
                               access_token[0].access_token)
        res = response.json()
        if res.get('errorCode') == M_PESA_TOKEN_EXPIRED:
            MpesaAuth.objects.all().delete()
            create_token()
            response = m_pesa_http(url, method, payload,
                                   access_token[0].access_token)

        if not status.is_success(response.status_code):
            raise ValidationError(str(res))

        return res

    def beyonic_withdraw(self, **kwargs):
        transaction = self.model()
        REQUIRED_ERROR = error_messages.REQUIRED
        errors = {
            'phonenumber': REQUIRED_ERROR.format('phonenumber is ') if not kwargs.get('phonenumber') else None,
            'amount': REQUIRED_ERROR.format('amount is ') if not kwargs.get('amount') else None,
            'currency': REQUIRED_ERROR.format('currency is ') if not kwargs.get('currency') else None,
            'description': REQUIRED_ERROR.format('description is ') if not kwargs.get('description') else None,
            'callback_url': REQUIRED_ERROR.format('callback_url is ') if not kwargs.get('callback_url') else None,
            'first_name': REQUIRED_ERROR.format('first_name is ') if not kwargs.get('first_name') else None,
            'last_name': REQUIRED_ERROR.format('last_name is ') if not kwargs.get('last_name') else None,
            'payment_type': REQUIRED_ERROR.format('payment_type is ') if not kwargs.get('payment_type') else None,
            'metadata': REQUIRED_ERROR.format('metadata is ') if not kwargs.get('metadata') else None,
        }

        metadata = kwargs.get('metadata') if isinstance(
            kwargs.get('metadata'), dict) else {}
        errors['wallet_id'] = REQUIRED_ERROR.format('wallet id is ') \
            if not (metadata.get('crypto_wallet_id') or metadata.get('fiat_wallet_id')) else None
        errors['tx_fee'] = REQUIRED_ERROR.format(
            'fee is ') if metadata.get('tx_fee') is None else None
        errors['fx_fee'] = REQUIRED_ERROR.format(
            'fx fee is ') if metadata.get('fx_fee') is None else None
        errors['fx_rate'] = REQUIRED_ERROR.format(
            'fx rate is ') if metadata.get('fx_rate') is None else None
        errors['target_currency'] = REQUIRED_ERROR.format(
            'target currency is ') if not metadata.get('target_currency') else None
        errors['source_amount'] = REQUIRED_ERROR.format(
            'source amount is ') if metadata.get('source_amount') is None else None
        errors['source_total_amount'] = REQUIRED_ERROR.format(
            'source total amount is ') if metadata.get('source_total_amount') is None else None
        errors['target_amount'] = REQUIRED_ERROR.format(
            'target amount is ') if metadata.get('target_amount') is None else None

        tx_crypto_wallet_id = metadata.get("crypto_wallet_id")
        tx_fiat_wallet_id = metadata.get("fiat_wallet_id")

        source_wallet = CryptoWallet.objects.get(id=tx_crypto_wallet_id) if tx_crypto_wallet_id \
            else FiatWallet.objects.get(id=tx_fiat_wallet_id)

        errors['amount'] = error_messages.INSUFFICIENT_FUNDS if \
            source_wallet.balance.amount < to_decimal(metadata.get('source_total_amount')) else None

        if len(remove_dict_none_values(errors)) != 0:
            raise ValidationError(str(errors))

        source_wallet.balance.amount -= to_decimal(
            metadata.get('source_total_amount'))

        transaction.type = constants.WITHDRAW
        transaction.wallet_id = kwargs.get('crypto_wallet_id')
        transaction.transaction_id = uuid.uuid4().hex
        transaction.source_currency = source_wallet.currency
        transaction.target_currency = metadata.get('target_currency')
        transaction.fee = to_decimal(metadata.get('tx_fee'))
        transaction.fx_fee = to_decimal(metadata.get('fx_fee'))
        transaction.fx_rate = to_decimal(metadata.get('fx_rate'))
        transaction.source_amount = to_decimal(kwargs.get('amount'))
        transaction.source_total_amount = to_decimal(
            metadata.get('source_total_amount'))
        transaction.target_amount = to_decimal(metadata.get('target_amount'))
        transaction.source_address = get_object_attr(
            source_wallet, 'address', get_object_attr(source_wallet, 'number'))
        transaction.target_address = kwargs.get('phonenumber')
        transaction.description = kwargs.get('description')
        transaction.state = self.model.ProcessingState.PROCESSING.label
        transaction.sender = source_wallet.user

        payload = {
            'phonenumber': kwargs.get('phonenumber'),
            'amount': metadata.get('target_amount'),
            'currency': kwargs.get('currency'),
            'description': kwargs.get('description'),
            'callback_url': kwargs.get('callback_url'),
            'first_name': kwargs.get('first_name'),
            'last_name': kwargs.get('last_name'),
            'payment_type': kwargs.get('payment_type'),
            'send_instructions': kwargs.get('send_instructions'),
            "metadata": {
                "tx_id": str(transaction.id),
                **({"crypto_wallet_id": tx_crypto_wallet_id} if tx_crypto_wallet_id else {}),
                **({"fiat_wallet_id": tx_fiat_wallet_id} if tx_fiat_wallet_id else {}),
            }

        }
        response = http_request(
            url=f'{settings.BEYONIC_API}/payments',
            method='POST',
            data=json.dumps(payload),
            headers={
                'Authorization': f'Token {settings.BEYONIC_API_TOKEN}',
                'Content-Type': 'application/json'
            }
        )

        if not status.is_success(response.status_code):
            raise ValidationError(str(response.json()))

        source_wallet.save()
        transaction.save(using=self._db)

        return response.json()

    def update_withdraw_transaction(self, **kwargs):
        REQUIRED_ERROR = error_messages.REQUIRED
        errors = {}
        data = kwargs.get('data') if isinstance(
            kwargs.get('data'), dict) else {}
        metadata = data.get('metadata') if isinstance(
            data.get('metadata'), dict) else {}

        errors['data'] = REQUIRED_ERROR.format('data is ') if not kwargs.get(
            'data') or not isinstance(kwargs.get('data'), dict) else None
        errors['currency'] = REQUIRED_ERROR.format(
            'currency is ') if not data.get('currency') else None
        errors['event'] = REQUIRED_ERROR.format(
            'event is ') if not kwargs.get('event') else None
        errors['metadata'] = REQUIRED_ERROR.format(
            'metadata is ') if not data.get('metadata') else None
        errors['id'] = REQUIRED_ERROR.format(
            'id is ') if not data.get('id') else None
        errors['wallet_id'] = REQUIRED_ERROR.format('wallet id is ') \
            if not (metadata.get('crypto_wallet_id') or metadata.get('fiat_wallet_id')) else None

        if len(remove_dict_none_values(errors)) != 0:
            raise ValidationError(str(errors))

        tx_state = data.get("state") or data.get("status")
        tx_id = metadata.get('tx_id')
        tx_crypto_wallet_id = metadata.get("crypto_wallet_id")
        tx_fiat_wallet_id = metadata.get("fiat_wallet_id")
        transaction = self.model.objects.get(id=tx_id)
        user_wallet = CryptoWallet.objects.get(id=tx_crypto_wallet_id) if tx_crypto_wallet_id \
            else FiatWallet.objects.get(id=tx_fiat_wallet_id)

        if transaction.state in [self.model.ProcessingState.DONE.label, self.model.ProcessingState.FAILED.label]:
            raise IntegrityError(f'this transaction {tx_id}')

        if tx_state in ["processed", "success", "successful"]:
            transaction.state = self.model.ProcessingState.DONE.label
        elif tx_state in ["rejected", "processed_with_errors", "cancelled"]:
            transaction.state = self.model.ProcessingState.FAILED.label
            user_wallet.balance.amount += transaction.source_total_amount.amount
            user_wallet.save()

        if transaction.state in [self.model.ProcessingState.DONE.label, self.model.ProcessingState.FAILED.label]:
            transaction.receiver = transaction.sender
            transaction.save(using=self._db)

        return transaction

    def create_topup_transaction(self, **kwargs):
        transaction = self.model()
        body = kwargs.get('Body')
        data = body.get('stkCallback')
        callback_data = data.get('CallbackMetadata') if isinstance(
            data.get('CallbackMetadata'), dict) else {}
        item_data = callback_data.get('Item')

        tx_state = data.get("ResultCode")
        if tx_state != 0:
            return topup_failed(self, body, data, transaction)
        return topup_success(self, data, item_data, transaction, tx_state)

    def send_crypto_funds(self, user=None, **kwargs):
        (requests, errors) = ([], {})
        if not kwargs.get('wallet_id'):
            errors['wallet_id'] = error_messages.REQUIRED.format(
                'wallet ID is ')

        if not kwargs.get('data') \
                or not isinstance(kwargs.get('data'), list)\
                or (isinstance(kwargs.get('data'), list) and not len(kwargs.get('data'))):
            errors['data'] = error_messages.REQUIRED.format('request data is ')

        if isinstance(kwargs.get('data'), list) and len(kwargs.get('data')):
            for data in kwargs.get('data'):
                errors['address'] = error_messages.REQUIRED.format(
                    'recipient address is ') if not data.get('address') else None
                errors['amount'] = error_messages.REQUIRED.format(
                    'amount is ') if not data.get('amount') else None

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

        checksum = CYBAVOChecksum(
            secret=master_wallet.api_secret, payload=payload).build()
        response = http_request(
            url=f'{settings.THRESH0LD_API}/v1/sofa/wallets/{master_wallet.wallet_id}/sender/transactions?r={checksum.r}&t={checksum.t}',
            method='POST',
            data=payload,
            headers={'X-API-CODE': master_wallet.api_token,
                     'X-CHECKSUM': str(checksum), }
        )

        if not status.is_success(response.status_code):
            raise ValidationError(str(response.json()))

        return response.json()

    def create_or_update_crypto_transaction(self, **kwargs):
        tx_model = self.model
        tx_state = tx_model.get_transaction_state(
            kwargs.get('state')).get('label')
        tx_type = tx_model.get_transaction_type(
            kwargs.get('type')).get('label')
        tx_processing_state = tx_model.get_transaction_processing_state(
            kwargs.get('processing_state')).get('label')

        try:
            transaction = tx_model.objects.get(order_id=kwargs.get('order_id'), type__iexact=tx_type) if kwargs.get('order_id') \
                else tx_model.objects.get(transaction_id=kwargs.get('txid'), vout_index=kwargs.get('vout_index'), type__iexact=tx_type)
        except tx_model.DoesNotExist:
            transaction = tx_model()

        tx_fee = to_decimal(kwargs.get('fee', transaction.fee.amount)) * \
            (1 / 10**to_decimal(kwargs.get('decimal')))
        tx_amount = to_decimal(kwargs.get(
            'amount', transaction.amount.amount)) * (1 / 10**to_decimal(kwargs.get('decimal')))
        tx_total_amount = kwargs.get('total_amount', tx_amount + tx_fee)

        crypto_wallets = CryptoWallet.objects.filter(wallet_id=kwargs.get('wallet_id'),
                                                     address__in=[kwargs.get('source_address'), kwargs.get('target_address')])
        if len(crypto_wallets):
            for crypto_wallet in crypto_wallets:
                transaction.sender = get_object_attr(
                    crypto_wallet, "user") if crypto_wallet.address == kwargs.get('source_address') else None
                transaction.receiver = get_object_attr(
                    crypto_wallet, "user") if crypto_wallet.address == kwargs.get('target_address') else None
                if tx_type == str(tx_model.Types.WITHDRAW.label) and crypto_wallet.address == kwargs.get('source_address'):
                    crypto_wallet.balance.amount -= tx_total_amount  # debit sender wallet

                if tx_type == str(tx_model.Types.DEPOSIT.label) and crypto_wallet.address == kwargs.get('target_address'):
                    crypto_wallet.balance.amount += tx_amount  # credit receiver wallet

            if not transaction.is_balance_updated and tx_processing_state == str(tx_model.ProcessingState.DONE.label)\
                and (tx_type == str(tx_model.Types.DEPOSIT.label)
                     or (tx_type == str(tx_model.Types.WITHDRAW.label) and tx_state == str(tx_model.State.IN_CHAIN.label))
                     ):
                CryptoWallet.objects.bulk_update(
                    crypto_wallets, fields=['balance'])
                transaction.is_balance_updated = True

        transaction.type = tx_type
        transaction.wallet_id = kwargs.get('wallet_id', transaction.wallet_id)
        transaction.order_id = kwargs.get('order_id', transaction.order_id)
        transaction.serial = kwargs.get('serial', transaction.serial)
        transaction.vout_index = kwargs.get(
            'vout_index', transaction.vout_index)
        transaction.transaction_id = kwargs.get(
            'txid', kwargs.get('transaction_id', transaction.transaction_id))
        transaction.currency = kwargs.get("currency", constants.BTC)
        transaction.fee = tx_fee or 0
        transaction.amount = tx_amount or 0
        transaction.total_amount = tx_total_amount
        transaction.source_address = kwargs.get(
            'source_address', transaction.source_address)
        transaction.target_address = kwargs.get(
            'target_address', transaction.target_address)
        transaction.description = kwargs.get(
            'description', transaction.description)
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

    def calculate_user_tx_total_amount(self, user):
        daily_tx_total_amount, weekly_tx_total_amount, monthly_tx_total_amount = (0, 0, 0)
        utc = datetime.timezone.utc
        today = datetime.datetime.utcnow()
        hms = datetime.timedelta(hours=today.hour, minutes=today.minute, seconds=today.second)

        daily_range = [today - hms, (today - hms) + datetime.timedelta(hours=23, minutes=59, seconds=59)]
        weekly_range = [
            today - hms - dateutil.relativedelta.relativedelta(weeks=1),
            (today - hms) + datetime.timedelta(hours=23, minutes=59, seconds=59)
        ]
        monthly_range = [
            today - hms - dateutil.relativedelta.relativedelta(months=1),
            (today - hms) + datetime.timedelta(hours=23, minutes=59, seconds=59)
        ]
        for tx in self.model.objects.filter(sender=user, created_at__range=monthly_range):
            amount = 0
            if tx.source_currency == user.local_currency:
                amount = tx.source_total_amount.amount
            else:
                currency_exchange = CurrencyExchange.objects.convert(**{
                    'amount': tx.source_total_amount.amount,
                    'base_currency': tx.source_currency,
                    'currency': tx.target_currency,
                })
                amount = to_decimal(currency_exchange.get('total_amount'))

            if tx.created_at >= daily_range[0].astimezone(utc) and tx.created_at <= daily_range[1].astimezone(utc):
                daily_tx_total_amount += amount
                weekly_tx_total_amount += amount
                monthly_tx_total_amount += amount
            elif tx.created_at >= weekly_range[0].astimezone(utc) and tx.created_at <= weekly_range[1].astimezone(utc):
                weekly_tx_total_amount += amount
                monthly_tx_total_amount += amount
            else:
                monthly_tx_total_amount += amount

        user.daily_tx_total_amount = daily_tx_total_amount
        user.weekly_tx_total_amount = weekly_tx_total_amount
        user.monthly_tx_total_amount = monthly_tx_total_amount
        user.save()
        return user
