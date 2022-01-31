from django.db.models.signals import post_save
from django.dispatch import receiver


from bitlipa.resources import constants, events
from bitlipa.utils.get_object_attr import get_object_attr
from bitlipa.utils.format_number import format_number
from bitlipa.apps.transactions.models import Transaction
from bitlipa.apps.notifications.models import Notification


@receiver(post_save, sender=Transaction)
def send_notification(sender, instance, created, **kwargs):
    event_type = events.GENERAL
    if not created:
        return

    sender = get_object_attr(instance, 'sender')
    receiver = get_object_attr(instance, 'receiver')

    if instance.type == constants.INTERNAL_USERS_TRANSACTION:
        event_type = events.MONEY_RECEIVED
    if instance.type == constants.TOP_UP:
        event_type = events.TOP_UP
    if instance.type == constants.WITHDRAW:
        event_type = events.WITHDRAW

    if event_type and receiver and get_object_attr(receiver, 'firebase_token'):
        if sender and get_object_attr(sender, 'id') != receiver.id:
            sender_first_name = instance.sender.first_name
            sender_middle_name = instance.sender.middle_name
            sender_last_name = instance.sender.last_name
            target_amount_amount = instance.target_amount.amount
            sender_email = instance.sender.email
            target_currency = instance.target_currency

            notification = {
                'delivery_option': 'in_app',
                'emails': [receiver.email],
                'title': f'{sender_first_name or sender_middle_name or sender_last_name or sender_email} sent you money',
                'content': {
                    'body': get_object_attr(instance, 'description')
                    or f'{sender_first_name} {sender_last_name} sent you {format_number(target_amount_amount)} {target_currency}',
                    'event_type': event_type,
                    'image': instance.sender.picture_url,
                    'payload': {},
                    'save': True
                },
                'recipient_id': receiver.id,
                'image_url': instance.sender.picture_url
            }
            return Notification.objects.create_notification(user=sender, **notification)

        notification = {
            'delivery_option': 'in_app',
            'emails': [receiver.email],
            'title': 'You received money',
            'content': {
                'body': get_object_attr(instance, 'description')
                or f'You received {format_number(instance.target_amount.amount)} {instance.target_currency}',
                'event_type': event_type,
                'payload': {},
                'save': True
            },
            'recipient_id': receiver.id,
        }
        return Notification.objects.create_notification(user=sender, **notification)
