from bitlipa.resources import error_messages
from bitlipa.utils.to_decimal import to_decimal
from bitlipa.apps.fees.models import Fee
from bitlipa.apps.global_configs.models import GlobalConfig
from bitlipa.apps.transaction_limits.models import TransactionLimit


def calculate_fees(source_wallet, target_wallet, amount):
    tx_fee, fx_fee = 0, 0
    internal_funds_transfer_fee = Fee.objects.get_fee(name__iexact="internal funds transfer")
    currency_exchange_fee = Fee.objects.get_fee(name__iexact="currency exchange")

    if str(internal_funds_transfer_fee.type).upper() == str(Fee.Types.FLAT):
        tx_fee = internal_funds_transfer_fee.amount
    if str(internal_funds_transfer_fee.type).upper() == str(Fee.Types.PERCENTAGE):
        tx_fee = to_decimal((internal_funds_transfer_fee.amount * amount) / 100)

    if source_wallet.currency != target_wallet.currency:
        if str(currency_exchange_fee.type).upper() == str(Fee.Types.FLAT):
            fx_fee = currency_exchange_fee.amount
        if str(currency_exchange_fee.type).upper() == str(Fee.Types.PERCENTAGE):
            fx_fee = to_decimal((currency_exchange_fee.amount * amount) / 100)
    return tx_fee, fx_fee


def check_transaction_limits(user, amount):
    error_msg = ""
    base_currency = GlobalConfig.objects.filter(name__iexact='base currency').first()
    tx_limits = TransactionLimit.objects.filter(currency__iexact=user.local_currency or base_currency.data).filter()
    for tx_limit in tx_limits:
        if (tx_limit.frequency == TransactionLimit.FrequencyTypes.DAILY
                and user.daily_tx_total_amount + amount > tx_limit.amount)\
            or (tx_limit.frequency == TransactionLimit.FrequencyTypes.WEEKLY
                and user.weekly_tx_total_amount + amount > tx_limit.amount)\
            or (tx_limit.frequency == TransactionLimit.FrequencyTypes.MONTHLY
                and user.monthly_tx_total_amount + amount > tx_limit.amount):
            error_msg = error_messages.LIMIT_EXCEEDED.format(f'{tx_limit.frequency.lower()} ')
            break
    return error_msg
