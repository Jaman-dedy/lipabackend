from django.db.models.signals import post_save
from django.dispatch import receiver


from bitlipa.resources import constants, events
from bitlipa.utils.get_object_attr import get_object_attr
from bitlipa.utils.format_number import format_number
from bitlipa.apps.transactions.models import Transaction
from bitlipa.apps.notifications.models import Notification


@receiver(post_save, sender=Transaction)
def post_save_handler(sender, instance, created, **kwargs):
    notification_sender = get_object_attr(instance, 'sender')
    notification_receiver = get_object_attr(instance, 'receiver')

    if not (notification_receiver and get_object_attr(notification_receiver, 'firebase_token')):
        return

    event_type = events.MONEY_RECEIVED
    title = 'You received money'
    body = get_object_attr(instance, 'description')
    image_url = ''

    if instance.type == constants.INTERNAL_USERS_TRANSACTION:
        sender_name = notification_sender.first_name or notification_sender.middle_name or \
            notification_sender.last_name or notification_sender.phonenumber or notification_sender.email
        event_type = events.MONEY_RECEIVED
        body = f'{sender_name} sent you {instance.target_currency} {format_number(instance.target_amount.amount)}'
        image_url = get_object_attr(notification_sender, 'picture_url', '')

    if instance.type == constants.TOP_UP:
        event_type = events.TOP_UP
        body = f'You received {instance.target_currency} {format_number(instance.target_amount.amount)}'

    if instance.type == constants.WITHDRAW:
        event_type = events.WITHDRAW
        title = 'Successful withdrawal' if instance.state == Transaction.ProcessingState.DONE.label else 'Withdrawal failed'
        body = f'You have successfully withdrawn {instance.target_currency} {format_number(instance.target_amount.amount)}' \
            if instance.state == Transaction.ProcessingState.DONE.label \
            else f'Withdrawal of {instance.target_currency} {format_number(instance.target_amount.amount)} failed'

    notification = {
        'delivery_option': 'in_app',
        'emails': [notification_receiver.email],
        'title': title,
        'content': {
            'body': body,
            'event_type': event_type,
            'image': image_url,
            'payload': {},
        },
        'image_url': image_url,
        'save': True,
    }
    return Notification.objects.create_notification(user=notification_sender, **notification)
