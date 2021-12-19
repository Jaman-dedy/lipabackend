import datetime
from django.core.paginator import Paginator
from django.db import models
from django.core.exceptions import ValidationError

from bitlipa.resources import constants, error_messages
from bitlipa.apps.users.models import User
from bitlipa.utils.get_object_attr import get_object_attr
from bitlipa.utils.remove_dict_none_values import remove_dict_none_values
from bitlipa.utils.to_int import to_int
from bitlipa.utils.send_sms import send_sms
from bitlipa.utils.firebase_messaging import send_notification as send_push_notification


class NotificationsManager(models.Manager):
    def list(self, user=None, **kwargs):
        table_fields = {**kwargs}
        page = to_int(kwargs.get('page'), 1)
        per_page = to_int(kwargs.get('per_page'), constants.DB_ITEMS_LIMIT)

        for key in ['page', 'per_page', 'q']:
            table_fields.pop(key, None)  # remove fields not in the DB table

        query = None

        if kwargs.get('q'):
            for field in table_fields:
                query = query | models.Q(**{f'{field.replace("iexact", "icontains")}': kwargs.get('q')}) if query else\
                    models.Q(**{f'{field.replace("iexact", "icontains")}': kwargs.get('q')})
            query = models.Q(**{'deleted_at': None}) & query if query else models.Q(**{'deleted_at': None})
        else:
            query = models.Q(**{'deleted_at': None, **remove_dict_none_values(table_fields)})

        if get_object_attr(user, 'id'):
            query = query & models.Q(**{'recipient_id': get_object_attr(user, 'id')})

        object_list = self.model.objects.filter(query).order_by('-created_at')
        data = Paginator(object_list, per_page).page(page).object_list
        return {
            'data': data,
            'meta': {
                'page': page,
                'per_page': per_page,
                'total': object_list.count()
            }
        }

    def create_notification(self, user, **kwargs):
        notification = self.model()

        if not kwargs.get('title'):
            raise ValidationError(error_messages.REQUIRED.format('Notification title is '))
        if not kwargs.get('content'):
            raise ValidationError(error_messages.REQUIRED.format('Notification content is '))
        if not kwargs.get('delivery_option'):
            raise ValidationError(error_messages.REQUIRED.format('Notification delivery mode is '))

        if kwargs.get('delivery_option') == 'sms':
            if not kwargs.get('phonenumber'):
                raise ValidationError(error_messages.REQUIRED.format('phone number is '))
            send_sms(kwargs.get('phonenumber'), message=kwargs.get('content'))

        if kwargs.get('delivery_option') == 'in_app':
            if not isinstance(kwargs.get('emails'), list) or not len(kwargs.get('emails')):
                raise ValidationError(error_messages.REQUIRED.format('recipient emails are '))
            if not isinstance(kwargs.get('content'), dict) or not len(kwargs.get('content')):
                raise ValidationError(error_messages.REQUIRED.format('notification content is '))
            if not kwargs.get('content').get('event_type'):
                raise ValidationError(error_messages.REQUIRED.format('event type is '))

            data = {
                'title': kwargs.get('title'),
                'body': kwargs.get('content').get('body'),
                'icon': kwargs.get('content').get('icon'),
                'image': kwargs.get('content').get('image') or kwargs.get('image_url'),
                'payload': kwargs.get('content').get('payload'),
            }
            recipients = User.objects.filter(email__in=kwargs.get('emails')).exclude(firebase_token=None).values_list('firebase_token', flat=True)
            if len(list(recipients)):
                send_push_notification(list(recipients), kwargs.get('content').get('event_type'), data)

        notification.sender = user
        notification.recipient_id = kwargs.get('recipient_id') or None
        notification.title = kwargs.get('title')
        notification.content = kwargs.get('content') if kwargs.get('delivery_option') != 'in_app' else kwargs.get('content').get('body')
        notification.delivery_option = kwargs.get('delivery_option')
        notification.image_url = kwargs.get('image_url')

        if kwargs.get('save') is not False:
            notification.save(using=self._db)

        return notification

    def update(self, id=None, **kwargs):
        notification = self.model.objects.get(id=id)

        notification.title = kwargs.get('title') or notification.title
        notification.content = kwargs.get('content') or notification.content
        notification.delivery_option = kwargs.get('delivery_option') or notification.delivery_option
        notification.image_url = kwargs.get('image_url') or notification.image_url

        notification.save(using=self._db)
        return notification

    def delete(self, id=None, user=None):
        notification = self.model.objects.get(id=id) \
            if get_object_attr(user, "is_admin")\
            else self.model.objects.get(id=id, recipient_id=get_object_attr(user, "id"))
        notification.deleted_at = datetime.datetime.now()
        notification.save(using=self._db)
        return notification
