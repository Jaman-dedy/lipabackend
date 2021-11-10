from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework import status


from bitlipa.utils.http_request import http_request


def login(**kwargs):
    payload = f'username={kwargs.get("username") or settings.ENIGMA_USERNAME}&'
    payload += f'password={kwargs.get("password") or settings.ENIGMA_PASSWORD}'

    response = http_request(
        url=f'{settings.ENIGMA_API_URL}/auth',
        method='PUT',
        data=payload,
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )

    if not status.is_success(response.status_code):
        raise ValidationError(response.json())

    return response.json()
