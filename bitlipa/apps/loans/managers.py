from contextlib import suppress
from datetime import datetime
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.db import models


from bitlipa.resources import constants, events
from bitlipa.resources import error_messages
from bitlipa.utils.to_int import to_int
from bitlipa.utils.to_decimal import to_decimal
from bitlipa.utils.remove_dict_none_values import remove_dict_none_values
from bitlipa.apps.users.models import User
from bitlipa.apps.users.serializers import BasicUserSerializer
from bitlipa.apps.global_configs.models import GlobalConfig
from bitlipa.apps.fiat_wallets.models import FiatWallet
from bitlipa.apps.notifications.models import Notification


class LoanManager(models.Manager):
    def list(self, **kwargs):
        page = to_int(kwargs.get('page'), 1)
        per_page = to_int(kwargs.get('per_page'), constants.DB_ITEMS_LIMIT)
        table_fields = {**kwargs, 'deleted_at': None}

        for key in ['page', 'per_page']:
            table_fields.pop(key, None)  # remove fields not in the DB table

        object_list = self.model.objects.filter(**{
            'deleted_at': None, **remove_dict_none_values(table_fields)}).order_by('-created_at')

        return {
            'data': Paginator(object_list, per_page).page(page).object_list,
            'meta': {
                'page': page,
                'per_page': per_page,
                'total': object_list.count()
            }
        }

    def create_loan(self, **kwargs):
        (loans, fiat_wallets, errors) = ([], [], {})

        if not isinstance(kwargs.get('beneficiaries'), list) or not len(kwargs.get('beneficiaries')):
            errors['beneficiaries'] = error_messages.REQUIRED.format('loan beneficiaries are ')

        if not isinstance(kwargs.get('limit_amount'), (int, float)):
            errors['limit_amount'] = error_messages.REQUIRED.format('loan limit is ')

        if len(remove_dict_none_values(errors)) != 0:
            raise ValidationError(str(errors))

        users = User.objects.filter(id__in=kwargs.get('beneficiaries'))
        beneficiaries = BasicUserSerializer(users, context={'include_wallets': True}, many=True).data

        if not len(beneficiaries):
            errors['beneficiaries'] = error_messages.NOT_FOUND.format('loan beneficiaries ')
            raise ValidationError(str(errors))

        currency = kwargs.get('currency')
        base_currency = GlobalConfig.objects.filter(name__iexact='base currency').first()
        supported_currencies = GlobalConfig.objects.filter(name__iexact='supported currencies').first()

        if str(currency).upper() not in list(map(str.upper, supported_currencies.data)):
            currency = base_currency.data

        for beneficiary in beneficiaries:
            (loan, fiat_wallet) = (self.model(), FiatWallet())
            fiat_wallet.name = 'Loan wallet'
            fiat_wallet.type = FiatWallet.Types.LOAN
            fiat_wallet.number = f'{beneficiary.get("phonenumber")}-{len(beneficiary.get("fiat_wallets")) + 1}'
            fiat_wallet.currency = currency
            fiat_wallet.user_id = beneficiary.get('id')
            fiat_wallets.append(fiat_wallet)

            loan.wallet = fiat_wallet
            loan.beneficiary_id = beneficiary.get('id')
            loan.currency = currency
            loan.limit_amount = kwargs.get('limit_amount')
            loan.borrowed_amount = kwargs.get('borrowed_amount')
            loan.description = kwargs.get('description')
            loans.append(loan)

        notification_receivers = list(map(lambda loan: loan.beneficiary.email, loans))
        event_type = events.TOP_UP
        title = 'Loan wallet created'
        body = kwargs.get('description') or 'Your loan wallet has been created'

        notification = {
            'delivery_option': 'in_app',
            'emails': notification_receivers,
            'title': title,
            'content': {'body': body, 'event_type': event_type, 'image': '', 'payload': {}},
            'image_url': '',
            'save': False,
        }
        FiatWallet.objects.bulk_create(fiat_wallets)
        loans = self.model.objects.bulk_create(loans)
        with suppress(Exception):
            Notification.objects.create_notification(user=None, **notification)
        return loans

    def get_loan(self, **kwargs):
        try:
            loan = self.model.objects.get(**kwargs)
            return loan
        except self.model.DoesNotExist:
            return self.model(amount=to_decimal(0))

    def update(self, id=None, **kwargs):
        errors = {}
        loan = self.model.objects.get(id=id, deleted_at=None)

        if len(remove_dict_none_values(errors)) != 0:
            raise ValidationError(str(errors))

        currency = kwargs.get('currency', loan.currency)
        base_currency = GlobalConfig.objects.filter(name__iexact='base currency').first()
        supported_currencies = GlobalConfig.objects.filter(name__iexact='supported currencies').first()

        if str(currency).upper() not in list(map(str.upper, supported_currencies.data)):
            currency = base_currency.data

        if loan.wallet:
            loan.wallet.balance = kwargs.get('limit_amount', loan.limit_amount)
            loan.wallet.save()
        else:
            fiat_wallet = FiatWallet()
            fiat_wallet.name = 'Loan wallet'
            fiat_wallet.type = FiatWallet.Types.LOAN
            fiat_wallet.balance = kwargs.get('limit_amount', loan.limit_amount)
            fiat_wallet.number = f'{loan.beneficiary.phonenumber}-{len(loan.beneficiary.get("fiat_wallets")) + 1}'
            fiat_wallet.currency = currency
            fiat_wallet.user_id = loan.beneficiary.get('id')
            fiat_wallet.save()
            loan.wallet = fiat_wallet

        loan.currency = currency
        loan.limit_amount = kwargs.get('limit_amount', loan.limit_amount)
        loan.borrowed_amount = kwargs.get('borrowed_amount', loan.borrowed_amount)
        loan.description = kwargs.get('description', loan.description)

        loan.save(using=self._db)
        return loan

    def remove(self, id=None):
        loan = self.model.objects.get(id=id, deleted_at=None)
        loan.deleted_at = datetime.now()
        loan.save(using=self._db)
        return loan
