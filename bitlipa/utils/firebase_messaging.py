import datetime
import json
import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings

from bitlipa.resources.events import GENERAL


class PushNotification:
    def __init__(self):
        self.app = None

    def initialize_app(self):
        service_account = eval(settings.FIREBASE_SERVICE_ACCOUNT)
        cred = credentials.Certificate(service_account)
        self.app = firebase_admin.initialize_app(cred)

    def send(self, tokens, event_type, data):
        notification_data = {
            **data,
            'event_type': event_type or GENERAL,
            'title': data.get('title') or data.get('event_type'),
            'body': data.get('body') or '',
            'icon': data.get('icon') or '@mipmap/ic_launcher',
            'color': data.get('color') or '#00343D',
            'priority': data.get('priority') or 'max',
            'visibility': data.get('visibility') or 'public',
            'image': data.get('image') or '',
            'payload': json.dumps(data.get('payload')) if isinstance(data.get('payload'), dict) else None
        }
        notification = {
            'title': data.get('title') or data.get('event_type'),
            'body': data.get('body') or '',
            'icon': data.get('icon') or '@mipmap/ic_launcher',
            'color': data.get('color') or '#00343D',
            'priority': data.get('priority') or 'max',
            'visibility': data.get('visibility') or 'public',
            'image': data.get('image') or '',
        }

        android_notification = messaging.AndroidConfig(
            ttl=datetime.timedelta(days=1),
            notification=messaging.AndroidNotification(**notification),
            data=notification_data)

        message = messaging.MulticastMessage(android=android_notification, tokens=tokens)
        response = messaging.send_multicast(multicast_message=message, app=self.app)
        if response.failure_count > 0:
            responses = response.responses
            failed_tokens = []
            for idx, resp in enumerate(responses):
                if not resp.success:
                    # The order of responses corresponds to the order of the registration tokens.
                    failed_tokens.append(tokens[idx])
            return failed_tokens
            # [END send_multicast_error]
