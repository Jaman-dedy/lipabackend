from djmoney.models.fields import MoneyField
from django.db import models
from uuid import uuid4
from django.utils.translation import gettext_lazy as _

from bitlipa.apps.users.models import User
from .managers import TransactionManager


class Transaction(models.Model):

    class Types(models.TextChoices):
        DEPOSIT = '1', _('Deposit')
        WITHDRAW = '2', _('Withdraw')
        COLLECT = '3', _('Collect')
        AIRDROP = '4', _('Airdrop')
        ALL = '-1', _('All')

    class State(models.TextChoices):
        INIT = '0', _('Init')
        PROCESSING = '1', _('Processing')
        IN_POOL = '2', _('TXID in pool')
        IN_CHAIN = '3', _('TXID in chain')
        DONE = '4', _('Done')
        FAILED = '5', _('Failed')
        CANCELLED = '8', _('Cancelled')
        DROPPED = '10', _('Dropped')

    class ProcessingState(models.TextChoices):
        IN_POOL = '0', _('TXID in pool')
        IN_CHAIN = '1', _('TXID in chain')
        DONE = '2', _('Done')

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    sender = models.ForeignKey(User, related_name='sender_id', verbose_name=_("sender"), on_delete=models.DO_NOTHING, null=True)
    receiver = models.ForeignKey(User, related_name='receiver_id', verbose_name=_("receiver"), on_delete=models.DO_NOTHING, null=True)
    type = models.CharField(verbose_name=_("transaction type"), max_length=30, blank=True, null=True)
    wallet_id = models.CharField(verbose_name=_("wallet ID"), max_length=30, blank=True, null=True)
    order_id = models.CharField(verbose_name=_("order ID"), max_length=30, blank=True, null=True)
    serial = models.CharField(verbose_name=_("serial number"), max_length=100, blank=True, null=True)
    vout_index = models.CharField(verbose_name=_("index of vout"), max_length=100, blank=True, null=True)
    transaction_id = models.CharField(verbose_name=_("transaction ID"), max_length=100, blank=True, null=True)
    from_currency = models.CharField(verbose_name=_("source currency"), max_length=30, blank=True, null=True)
    to_currency = models.CharField(verbose_name=_("target currency"), max_length=30, blank=True, null=True)
    fee = MoneyField(verbose_name=_("transaction fee"),
                     blank=False,
                     null=False,
                     default=0,
                     max_digits=36,
                     decimal_places=18,
                     currency_field_name='from_currency')
    fx_fee = MoneyField(verbose_name=_("currency exchange fee"),
                        blank=False,
                        null=False,
                        default=0,
                        max_digits=36,
                        decimal_places=18,
                        currency_field_name='to_currency')
    amount = MoneyField(verbose_name=_("transaction amount"),
                        blank=False,
                        null=False,
                        default=0,
                        max_digits=36,
                        decimal_places=18,
                        currency_field_name='to_currency')
    total_amount = MoneyField(verbose_name=_("transaction total amount"),
                              blank=False,
                              null=False,
                              default=0,
                              max_digits=36,
                              decimal_places=18,
                              currency_field_name='from_currency')
    from_address = models.CharField(verbose_name=_("source crypto wallet address"), max_length=100, blank=True, null=True)
    to_address = models.CharField(verbose_name=_("destination crypto wallet address"), max_length=100, blank=True, null=True)
    description = models.TextField(verbose_name=_("transaction description"), blank=True, null=True)
    state = models.CharField(verbose_name=_("transaction state"),
                             max_length=30,
                             choices=State.choices,
                             default=State.PROCESSING.label,
                             blank=False,
                             null=False)
    is_balance_updated = models.BooleanField(verbose_name="is sender or receiver balance updated",
                                             blank=False, null=False, default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_("created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("updated at"))
    deleted_at = models.DateTimeField(auto_now=False, verbose_name=_("deleted at"), null=True)

    objects = TransactionManager()

    class Meta:
        db_table = "transactions"
        ordering = ("created_at", "updated_at")

    def get_transaction_type(value=None):
        tx_type = {}
        for (_value, _label) in Transaction.Types.choices:
            if _value == str(value).lower() or str(_label).lower() == str(value).lower():
                tx_type = {'value': str(_value), 'label': str(_label)}
                break
        return tx_type

    def get_transaction_state(value=None):
        tx_state = {}
        for (_value, _label) in Transaction.State.choices:
            if _value == str(value).lower() or str(_label).lower() == str(value).lower():
                tx_state = {'value': str(_value), 'label': str(_label)}
                break
        return tx_state

    def get_transaction_processing_state(value=None):
        tx_state = {}
        for (_value, _label) in Transaction.ProcessingState.choices:
            if _value == str(value).lower() or str(_label).lower() == str(value).lower():
                tx_state = {'value': str(_value), 'label': str(_label)}
                break
        return tx_state
