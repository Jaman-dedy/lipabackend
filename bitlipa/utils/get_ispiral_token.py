
from django.conf import settings
from bitlipa.utils.http_request import http_request
from rest_framework import status
from django.core.exceptions import ValidationError
import datetime


def create_token() -> any:
    payload = f'client_id={settings.KYC_ISPIRAL_CLIENT_ID}&'
    payload += f'client_secret={settings.KYC_ISPIRAL_CLIENT_SECRET}&'
    payload += f'grant_type={settings.KYC_ISPIRAL_GRANT_TYPE}'
    response = http_request(
        url=f'{settings.KYC_ISPIRAL_API}/token',
        method='POST',
        data=payload,
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )

    if not status.is_success(response.status_code):
        raise ValidationError(response.json())

    res = response.json()
    token = res.get('access_token')
    current_time = datetime.datetime.now()
    with open('ispiral.log', 'w+') as f:
        f.write(f'token: {token}\ncreated_at: {current_time.strftime("%m/%d/%y %H:%M:%S")}')
        f.close()

    return token


def get_token() -> str:
    try:
        token = ''
        created_at = ''
        with open('ispiral.log', 'r') as f:
            for line in f:
                if 'token: ' in line:
                    token = line.replace('token: ', '').strip()
                if 'created_at: ' in line:
                    created_at = line.replace('created_at: ', '').strip()
            f.close()

        if not token and not created_at:
            return create_token()

        actual_time = datetime.datetime.now()
        saved_time = datetime.datetime.strptime(created_at, '%m/%d/%y %H:%M:%S')
        expirty_time = actual_time - saved_time

        if expirty_time.total_seconds() > 57600:
            return create_token()
        return token
    except FileNotFoundError:
        return create_token()
