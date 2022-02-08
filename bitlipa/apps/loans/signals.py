from django.db.models.signals import post_save
from django.dispatch import receiver


from bitlipa.resources import events
from bitlipa.utils.get_object_attr import get_object_attr
from bitlipa.apps.loans.models import Loan
from bitlipa.apps.notifications.models import Notification


@receiver(post_save, sender=Loan)
def send_notification(sender, instance, created, **kwargs):
    notification_receiver = get_object_attr(instance, 'beneficiary')

    if not (notification_receiver and get_object_attr(notification_receiver, 'firebase_token')):
        return

    event_type = events.TOP_UP
    title = 'Loan wallet created' if created else 'Loan wallet updated'
    body = f'Your loan wallet has been created. Your loan limit is {instance.currency} {(instance.limit_amount)}' if created else \
        f'Your loan wallet has been updated. Your loan limit is {instance.currency} {(instance.limit_amount)}'

    notification = {
        'delivery_option': 'in_app',
        'emails': [notification_receiver.email],
        'title': title,
        'content': {
            'body': body,
            'event_type': event_type,
            'image': '',
            'payload': {},
        },
        'image_url': '',
        'save': False,
    }
    return Notification.objects.create_notification(user=None, **notification)
