from bitlipa.utils.http_request import http_request
from django.conf import settings

def m_pesa_http(url, method, payload, access_token):
    response = http_request(
        url=f'{settings.M_PESA_API}{url}',
        method=method,
        data=payload,
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    )
    return response