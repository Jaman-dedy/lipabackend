import firebase_admin
from firebase_admin import credentials, messaging

from django.conf import settings

cred = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT_FILE_PATH)
app = firebase_admin.initialize_app(cred)


def send_notification(tokens=[], data={}, eventType=None):
    notification = {'eventType': str(eventType), **data}

    message = messaging.MulticastMessage(
        data=notification,
        tokens=tokens,
    )
    response = messaging.send_multicast(multicast_message=message, app=app)
    if response.failure_count > 0:
        responses = response.responses
        failed_tokens = []
        for idx, resp in enumerate(responses):
            if not resp.success:
                # The order of responses corresponds to the order of the registration tokens.
                failed_tokens.append(tokens[idx])
        print('List of tokens that caused failures: {0}'.format(failed_tokens))
        # [END send_multicast_error]
