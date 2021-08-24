
from rest_framework import viewsets, status
from bitlipa.utils.http_response import http_response
import json
from rest_framework.decorators import action
from django.core.exceptions import ValidationError
from django.conf import settings

from bitlipa.utils.auth_util import AuthUtil
from bitlipa.resources import error_messages
from bitlipa.utils.http_request import http_request
from bitlipa.utils.get_ispiral_token import get_token


class IspiralKycViewSet(viewsets.ViewSet):
    """
    API endpoint that allows to check users's kyc .
    """

    @action(methods=['post'], detail=False, url_path='verify-document', url_name='verify_document')
    def verify_document(self, request):
        AuthUtil.is_auth(request)

        errors = dict()
        if not request.data.get('file'):
            errors['file'] = error_messages.REQUIRED.format('file is ')
        if not request.data.get('fileSupport'):
            errors['fileSupport'] = error_messages.REQUIRED.format('fileSupport is ')

        if len(errors) != 0:
            raise ValidationError(str(errors))

        payload = {
            'file': request.data.get('file'),
            'fileSupport': request.data.get('fileSupport')
        }

        payload = json.dumps(payload)

        response = http_request(
            url=f'{settings.KYC_ISPIRAL_API}/api/v2/service/documentVerification',
            method='POST',
            data=payload,
            headers={
                'Authorization': f'Bearer {get_token()}',
                'Content-Type': 'application/json'
            }
        )

        if not status.is_success(response.status_code):
            raise ValidationError(str(response.json()))
        return http_response(status=status.HTTP_201_CREATED, data=response.json())

    @action(methods=['post'], detail=False, url_path='negative-list', url_name='negative_list')
    def negative_list(self, request):
        AuthUtil.is_auth(request)

        errors = dict()
        if not request.data.get('acuris'):
            errors['acuris'] = error_messages.REQUIRED.format('acuris is ')
        acuris_data = request.data.get('acuris')
        if not acuris_data.get('firstname'):
            errors['firstname'] = error_messages.REQUIRED.format('firstname is ')
        if not acuris_data.get('middlename'):
            errors['middlename'] = error_messages.REQUIRED.format('middlename is ')
        if not acuris_data.get('lastname'):
            errors['lastname'] = error_messages.REQUIRED.format('lastname is ')

        if len(errors) != 0:
            raise ValidationError(str(errors))

        payload = {
            "acuris": {
                "firstname": acuris_data.get('firstname'),
                "middlename": acuris_data.get('middlename'),
                "lastname": acuris_data.get('lastname'),
                "dateOfBirth": acuris_data.get('dateOfBirth'),
                "address": acuris_data.get('address'),
                "city": acuris_data.get('city'),
                "country": acuris_data.get('country'),
                "postcode": acuris_data.get('postcode'),
                "companyName": acuris_data.get('companyName'),
                "vatNumber": acuris_data.get('vatNumber'),
                "threshold": acuris_data.get('threshold')
            }
        }

        response = http_request(
            url=f'{settings.KYC_ISPIRAL_API}/api/v2/service/personSearch',
            method='POST',
            json=payload,
            headers={
                'Authorization': f'Bearer {get_token()}',
                'Content-Type': 'application/json'
            }
        )

        if not status.is_success(response.status_code):
            raise ValidationError(response.content)
        return http_response(status=status.HTTP_201_CREATED, data=response.json())

    @action(methods=['post'], detail=False, url_path='fraud-risk', url_name='fraud_risk')
    def fraud_risk(self, request):
        AuthUtil.is_auth(request)

        errors = dict()
        if not request.data.get('email'):
            errors['email'] = error_messages.REQUIRED.format('email is ')

        email = request.data.get('email')
        device = request.data.get('device')
        billing = request.data.get('billing')
        credit_card = request.data.get('credit_card')

        if not email.get('address'):
            errors['address'] = error_messages.REQUIRED.format('address is ')

        if len(errors) != 0:
            raise ValidationError(str(errors))

        payload = {
            "device": {
                "ip_address": device.get('ip_address'),
                "user_agent": device.get('user_agent'),
                "accept_language": device.get('accept_language'),
                "session_age": device.get('session_age'),
                "session_id": device.get('session_id')
            },
            "email": {
                "address": email.get('address'),
                "domain": email.get('domain')
            },
            "billing": {
                "first_name": billing.get('first_name'),
                "last_name": billing.get('last_name'),
                "company": billing.get('company'),
                "address": billing.get('address'),
                "address_2": billing.get('address_2'),
                "city": billing.get('city'),
                "region": billing.get('region'),
                "country": billing.get('country'),
                "postal": billing.get('postal'),
                "phone_number": billing.get('phone_number'),
                "phone_country_code": billing.get('phone_country_code')
            },
            "credit_card": {
                "issuer_id_number": credit_card.get('issuer_id_number'),
                "last_4_digits": credit_card.get('last_4_digits'),
                "token": credit_card.get('token'),
                "bank_name": credit_card.get('bank_name'),
                "bank_phone_country_code": credit_card.get('bank_phone_country_code'),
                "bank_phone_number": credit_card.get('bank_phone_number'),
                "avs_result": credit_card.get('avs_result'),
                "cvv_result": credit_card.get('cvv_result')
            }
        }

        response = http_request(
            url=f'{settings.KYC_ISPIRAL_API}/api/v2/service/entityFraudScore',
            method='POST',
            json=payload,
            headers={
                'Authorization': f'Bearer {get_token()}',
                'Content-Type': 'application/json'
            }
        )

        if not status.is_success(response.status_code):
            raise ValidationError(response.content)
        return http_response(status=status.HTTP_201_CREATED, data=response.json())
