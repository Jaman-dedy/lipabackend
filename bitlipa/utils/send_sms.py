from django.conf import settings
from twilio.rest import Client


def send_sms(recipient, message="BitLipa"):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    if recipient:
        client.messages.create(to=recipient, from_=settings.TWILIO_NUMBER, body=message)
