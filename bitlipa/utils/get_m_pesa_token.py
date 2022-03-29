
from aiohttp import payload
from django.conf import settings
from bitlipa.utils.http_request import http_request
from rest_framework import status
from django.core.exceptions import ValidationError
from bitlipa.apps.mpesa_auth.models import MpesaAuth
import datetime


def create_token() -> any:
    mpesa_auth = MpesaAuth()
    auth=(
        settings.M_PESA_USERNAME,
        settings.M_PESA_SECRET
    )
    response = http_request(
        url=f'{settings.M_PESA_API}/oauth/v1/generate?grant_type=client_credentials',
        method='GET',
        auth=auth,
    )

    if not status.is_success(response.status_code):
        raise ValidationError(response.json())

    res = response.json()
    token = res.get('access_token')
    exp_time = res.get('expires_in')
    mpesa_auth.access_token = token
    mpesa_auth.expires_in = exp_time
    mpesa_auth.save()

    return response


# def get_token() -> str:
#     try:
#         token = ''
#         created_at = ''
#         with open('ispiral.log', 'r') as f:
#             for line in f:
#                 if 'token: ' in line:
#                     token = line.replace('token: ', '').strip()
#                 if 'created_at: ' in line:
#                     created_at = line.replace('created_at: ', '').strip()
#             f.close()

#         if not token and not created_at:
#             return create_token()

#         actual_time = datetime.datetime.now()
#         saved_time = datetime.datetime.strptime(created_at, '%m/%d/%y %H:%M:%S')
#         expirty_time = actual_time - saved_time

#         if expirty_time.total_seconds() > 57600:
#             return create_token()
#         return token
#     except FileNotFoundError:
#         return create_token()
