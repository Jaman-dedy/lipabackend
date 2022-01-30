from datetime import datetime, timezone
from django.conf import settings

from bitlipa.utils.logger import logger
from bitlipa.apps.fiat_wallets.models import FiatWallet
from .models import Loan


def update_loan_wallets_balance():
    today = datetime.now(timezone.utc)
    (loans, fiat_wallets) = ([], [])

    for loan in Loan.objects.filter(deleted_at=None):
        # TODO: use global settings to check update frequency
        if loan.wallet and today >= loan.updated_at and abs(today.day - loan.updated_at.day) > 0:
            loan.wallet.balance = loan.limit_amount
            loan.updated_at = today
            loans.append(loan)
            fiat_wallets.append(loan.wallet)

    FiatWallet.objects.bulk_update(fiat_wallets, ['balance'])
    Loan.objects.bulk_update(loans, ['updated_at'])

    if settings.DEBUG is True:
        logger(f'update loan wallets balance: {len(fiat_wallets)}', 'info')
        return
