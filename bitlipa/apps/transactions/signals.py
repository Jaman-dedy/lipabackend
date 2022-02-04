from django.db.models.signals import post_save
from django.dispatch import receiver


from bitlipa.resources import constants, events
from bitlipa.utils.get_object_attr import get_object_attr
from bitlipa.utils.format_number import format_number
from bitlipa.apps.transactions.models import Transaction
from bitlipa.apps.notifications.models import Notification


@receiver(post_save, sender=Transaction)
def send_notification(sender, instance, created, **kwargs):
    sender = get_object_attr(instance, 'sender')
    receiver = get_object_attr(instance, 'receiver')

    if not (receiver and get_object_attr(receiver, 'firebase_token')):
        return

    event_type = events.MONEY_RECEIVED
    title = 'You received money'
    body = get_object_attr(instance, 'description')
    image_url = ''

    if instance.type == constants.INTERNAL_USERS_TRANSACTION:
        sender_name = sender.first_name or sender.middle_name or sender.last_name or sender.phonenumber or sender.email
        event_type = events.MONEY_RECEIVED
        body = f'{sender_name} sent you {format_number(instance.target_amount.amount)} {instance.target_currency}'
        image_url = get_object_attr(sender, 'picture_url', '')

    if instance.type == constants.TOP_UP:
        event_type = events.TOP_UP
        body = f'You received {format_number(instance.target_amount.amount)} {instance.target_currency}'

    if instance.type == constants.WITHDRAW:
        event_type = events.WITHDRAW
        title = 'Successful withdrawal' if instance.state == Transaction.ProcessingState.DONE.label else 'Withdrawal failed'
        body = f'You have successfully withdrawn {format_number(instance.target_amount.amount)} {instance.target_currency}' \
            if instance.state == Transaction.ProcessingState.DONE.label \
            else f'Withdrawal of {format_number(instance.target_amount.amount)} {instance.target_currency} failed'

    notification = {
        'delivery_option': 'in_app',
        'emails': [receiver.email],
        'title': title,
        'content': {
            'body': body,
            'event_type': event_type,
            'image': image_url,
            'payload': {},
            'save': True
        },
        'recipient_id': receiver.id,
        'image_url': image_url
    }
    return Notification.objects.create_notification(user=sender, **notification)
