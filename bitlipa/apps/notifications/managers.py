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
from bitlipa.utils.firebase_messaging import PushNotification

push_notification = PushNotification()
push_notification.initialize_app()


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
        (notifications, recipients, errors) = ([], [], {})
        delivery_option = kwargs.get('delivery_option')
        errors['title'] = error_messages.REQUIRED.format('title is ') if not kwargs.get('title') else None
        errors['content'] = error_messages.REQUIRED.format('content is ') if not kwargs.get('content') else None
        errors['delivery_option'] = error_messages.REQUIRED.format('delivery option is ') \
            if not delivery_option else None
        errors['phonenumber'] = error_messages.REQUIRED.format('phone number is ') \
            if delivery_option == 'sms' and not kwargs.get('phonenumber') else None

        if delivery_option == 'in_app':
            errors['emails'] = error_messages.REQUIRED.format('recipient emails are ') \
                if not isinstance(kwargs.get('emails'), list) or not len(kwargs.get('emails')) else None
            errors['content'] = error_messages.REQUIRED.format('notification content is ') \
                if not isinstance(kwargs.get('content'), dict) or not len(kwargs.get('content')) else None
            errors['event_type'] = error_messages.REQUIRED.format('event type is ') \
                if errors['content'] or not kwargs.get('content').get('event_type') else None

        if len(remove_dict_none_values(errors)) != 0:
            raise ValidationError(str(errors))

        if isinstance(kwargs.get('emails'), list) and len(kwargs.get('emails')):
            recipients = User.objects.filter(email__in=kwargs.get('emails'))

        if delivery_option == 'sms':
            send_sms(kwargs.get('phonenumber'), message=kwargs.get('content'))

        if delivery_option == 'in_app':
            receivers = list(filter(lambda token: token is not None, map(lambda r: r.firebase_token, recipients)))
            if len(receivers):
                data = {
                    'title': kwargs.get('title'),
                    'body': kwargs.get('content').get('body'),
                    'icon': kwargs.get('content').get('icon'),
                    'image': kwargs.get('content').get('image') or kwargs.get('image_url'),
                    'payload': kwargs.get('content').get('payload'),
                }
                push_notification.send(receivers, kwargs.get('content').get('event_type'), data)

        for recipient in (recipients if len(recipients) else [None]):
            notification = self.model()
            notification.sender = user
            notification.recipient = recipient
            notification.title = kwargs.get('title')
            notification.content = kwargs.get('content') if delivery_option != 'in_app' \
                else kwargs.get('content').get('body')
            notification.delivery_option = delivery_option
            notification.image_url = kwargs.get('image_url')
            notifications.append(notification)

        if kwargs.get('save') is not False:
            self.model.objects.bulk_create(notifications)

        return notifications

    def update(self, id=None, user=None, **kwargs):
        notification = self.model.objects.get(id=id) \
            if get_object_attr(user, "is_admin")\
            else self.model.objects.get(id=id, recipient_id=get_object_attr(user, "id"))

        notification.title = kwargs.get('title') or notification.title
        notification.content = kwargs.get('content') or notification.content
        notification.delivery_option = kwargs.get('delivery_option') or notification.delivery_option
        notification.image_url = kwargs.get('image_url') or notification.image_url
        notification.status = kwargs.get('status') or notification.status

        notification.save(using=self._db)
        return notification

    def multi_update(self, user=None, **kwargs):
        ids = kwargs.get('IDs')
        if not isinstance(ids, list) or not len(ids):
            raise ValidationError(error_messages.REQUIRED.format('notification IDs are '))

        notifications = self.model.objects.filter(id__in=ids) \
            if get_object_attr(user, "is_admin")\
            else self.model.objects.filter(id__in=ids, recipient_id=get_object_attr(user, "id"))

        for notification in notifications:
            notification.title = kwargs.get('title') or notification.title
            notification.content = kwargs.get('content') or notification.content
            notification.delivery_option = kwargs.get('delivery_option') or notification.delivery_option
            notification.image_url = kwargs.get('image_url') or notification.image_url
            notification.status = kwargs.get('status') or notification.status

        self.model.objects.bulk_update(notifications, ['title', 'content', 'delivery_option', 'image_url', 'status'])
        return notifications

    def delete(self, id=None, user=None):
        notification = self.model.objects.get(id=id) \
            if get_object_attr(user, "is_admin")\
            else self.model.objects.get(id=id, recipient_id=get_object_attr(user, "id"))
        notification.deleted_at = datetime.datetime.now()
        notification.save(using=self._db)
        return notification
