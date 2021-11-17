from django.db.models.signals import post_save
from django.dispatch import receiver


from bitlipa.resources import constants, events
from bitlipa.utils.get_object_attr import get_object_attr
from bitlipa.utils.format_number import format_number
from bitlipa.utils.firebase_messaging import send_notification as send_push_notification
from bitlipa.apps.transactions.models import Transaction


@receiver(post_save, sender=Transaction)
def send_notification(sender, instance, created, **kwargs):
    if not created:
        return

    sender = get_object_attr(instance, 'sender')
    receiver = get_object_attr(instance, 'receiver')

    if instance.type == constants.INTERNAL_USERS_TRANSACTION and receiver and get_object_attr(receiver, 'firebase_token'):
        if sender and get_object_attr(sender, 'id') != receiver.id:
            data = {
                'title': f'{instance.sender.first_name or instance.sender.middle_name or instance.sender.last_name or instance.sender.email} sent you money',
                'body': f'{instance.sender.first_name} {instance.sender.last_name} sent you {format_number(instance.target_amount.amount)} {instance.target_currency}',
                'image': instance.sender.picture_url,
                'payload': {},
            }
            return send_push_notification([receiver.firebase_token], events.MONEY_RECEIVED, data)

        data = {
            'title': 'You received money',
            'body': f'You received {format_number(instance.target_amount.amount)} {instance.target_currency}',
            'payload': {},
        }
        return send_push_notification([receiver.firebase_token], events.MONEY_RECEIVED, data)
