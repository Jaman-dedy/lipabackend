import datetime
from django.core.paginator import Paginator
from django.db import models

from bitlipa.resources import constants
from bitlipa.utils.list_utils import filter_list
from bitlipa.utils.to_int import to_int
from bitlipa.utils.to_decimal import to_decimal
from bitlipa.utils.get_object_attr import get_object_attr
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

    def create_or_update_transaction(self, **kwargs):
        try:
            transaction = self.model.objects.get(transaction_id=kwargs.get('txid'),
                                                 vout_index=kwargs.get('vout_index'),
                                                 order_id=kwargs.get('order_id'))
        except self.model.DoesNotExist:
            transaction = self.model()

        tx_fees = to_decimal(kwargs.get('fees', transaction.fees.amount)) * (1 / 10**to_decimal(kwargs.get('decimal'), 8))
        tx_amount = to_decimal(kwargs.get('amount', transaction.amount.amount)) * (1 / 10**to_decimal(kwargs.get('decimal'), 8))
        tx_state = self.model.get_transaction_state(kwargs.get('state')).get('label')

        crypto_wallets = CryptoWallet.objects.filter(wallet_id=kwargs.get('wallet_id'),
                                                     address__in=[kwargs.get('from_address'), kwargs.get('to_address')])

        for crypto_wallet in crypto_wallets:
            if crypto_wallet.address == kwargs.get('from_address'):
                transaction.sender = get_object_attr(crypto_wallet, "user")
                crypto_wallet.balance.amount -= tx_amount  # debit sender wallet

            if crypto_wallet.address == kwargs.get('to_address'):
                transaction.receiver = get_object_attr(crypto_wallet, "user")
                crypto_wallet.balance.amount += tx_amount  # credit receiver wallet

        if len(crypto_wallets) and\
                not transaction.is_balance_updated and \
                str(kwargs.get('state')) == str(self.model.State.IN_CHAIN) and \
                str(kwargs.get('processing_state')) == str(self.model.ProcessingState.DONE):
            CryptoWallet.objects.bulk_update(crypto_wallets, fields=['balance'])
            transaction.is_balance_updated = True

        transaction.type = self.model.get_transaction_type(kwargs.get('type')).get('label')
        transaction.wallet_id = kwargs.get('wallet_id', transaction.wallet_id)
        transaction.order_id = kwargs.get('order_id', transaction.order_id)
        transaction.serial = kwargs.get('serial', transaction.serial)
        transaction.vout_index = kwargs.get('vout_index', transaction.vout_index)
        transaction.transaction_id = kwargs.get('txid', kwargs.get('transaction_id', transaction.transaction_id))
        transaction.currency = kwargs.get("currency", constants.BTC)
        transaction.fees = tx_fees or 0
        transaction.amount = tx_amount or 0
        transaction.total_amount = kwargs.get('total_amount', tx_amount + tx_fees)
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
