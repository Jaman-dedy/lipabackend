from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver


from bitlipa.resources import events
from bitlipa.utils.to_decimal import to_decimal
from bitlipa.utils.get_object_attr import get_object_attr
from bitlipa.apps.loans.models import Loan
from bitlipa.apps.notifications.models import Notification


@receiver(pre_save, sender=Loan)
def pre_save_handler(sender, instance, update_fields=None, **kwargs):
    try:
        instance._previous_instance = Loan.objects.get(id=instance.id)
    except Loan.DoesNotExist:
        instance._previous_instance = instance


@receiver(post_save, sender=Loan)
def post_save_handler(sender, instance, created, **kwargs):
    event_type, title, body = events.TOP_UP, '', ''
    previous_instance = instance._previous_instance
    notification_receiver = get_object_attr(instance, 'beneficiary')

    if not (notification_receiver and get_object_attr(notification_receiver, 'email')):
        return

    if created:
        title = 'Loan wallet created'
        body = 'Your loan wallet has been created.'

    if to_decimal(previous_instance.limit_amount) != to_decimal(instance.limit_amount):
        title = 'Loan wallet updated'
        body = f'Your loan wallet has been updated. Your loan limit is {instance.currency} {(instance.limit_amount)}'

    if to_decimal(previous_instance.borrowed_amount) and to_decimal(instance.borrowed_amount) == 0:
        title = 'Loan settled'
        body = f'Your loan of {previous_instance.currency} {(previous_instance.borrowed_amount)} has been settled.'

    if event_type and title and body:
        notification = {
            'delivery_option': 'in_app',
            'emails': [notification_receiver.email],
            'title': title,
            'content': {'body': body, 'event_type': event_type, 'image': '', 'payload': {}},
            'image_url': '',
            'save': True,
        }
        Notification.objects.create_notification(user=None, **notification)
