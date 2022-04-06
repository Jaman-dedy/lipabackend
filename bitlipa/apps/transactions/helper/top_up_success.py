from bitlipa.utils.get_object_attr import get_object_attr
from bitlipa.apps.crypto_wallets.models import CryptoWallet
from bitlipa.apps.fiat_wallets.models import FiatWallet
from bitlipa.resources import constants

def topup_success (self, data, item_data, transaction, tx_state):
    tx_crypto_wallet_id = ''
    tx_fiat_wallet_id = item_data[5].get('Value')
    # tx_fee = to_decimal(metadata.get('tx_fee'))
    # fx_fee = to_decimal(metadata.get('fx_fee'))
    # fx_rate = to_decimal(metadata.get('fx_rate'))
    source_amount = item_data[0].get('Value')
    source_total_amount = item_data[6].get('Value')
    target_amount = item_data[6].get('Value')

    user_wallet = CryptoWallet.objects.get(id=tx_crypto_wallet_id) if tx_crypto_wallet_id \
        else FiatWallet.objects.get(id=tx_fiat_wallet_id)
    
    source_currency = 'KES' if tx_fiat_wallet_id else data.get('source_currency')

    transaction.transaction_id = data.get('CheckoutRequestID')
    transaction.serial = data.get('MerchantRequestID')
    transaction.type = constants.TOP_UP
    transaction.wallet_id = get_object_attr(user_wallet, 'id')
    transaction.order_id = data.get('MerchantRequestID')
    transaction.source_currency = source_currency
    transaction.target_currency = user_wallet.currency
    transaction.description = data.get('ResultDesc')
    transaction.state = self.model.ProcessingState.DONE.label
    # transaction.fee = tx_fee
    # transaction.fx_fee = fx_fee
    # transaction.fx_rate = fx_rate
    transaction.source_amount = source_amount
    transaction.source_total_amount = source_total_amount
    transaction.target_amount = target_amount
    transaction.source_address = item_data[4].get('Value')
    transaction.target_address = get_object_attr(user_wallet, 'address') or get_object_attr(user_wallet, 'number')
    transaction.receiver = user_wallet.user
    transaction.is_balance_updated = True
    if tx_state in [0,"success", "successful"]:
        user_wallet.balance.amount += target_amount
        user_wallet.save()
        transaction.save(using=self._db)
    return transaction