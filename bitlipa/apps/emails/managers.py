from django.conf import settings
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.db import models


from bitlipa.resources import constants
from bitlipa.resources import error_messages
from bitlipa.utils.to_int import to_int
from bitlipa.utils.to_decimal import to_decimal
from bitlipa.utils.remove_dict_none_values import remove_dict_none_values


class EmailManager(models.Manager):
    def list(self, **kwargs):
        page = to_int(kwargs.get('page'), 1)
        per_page = to_int(kwargs.get('per_page'), constants.DB_ITEMS_LIMIT)
        table_fields = {**kwargs, 'deleted_at': None}

        for key in ['page', 'per_page']:
            table_fields.pop(key, None)  # remove fields not in the DB table

        object_list = self.model.objects.filter(**{
            'deleted_at': None, **remove_dict_none_values(table_fields)}).order_by('-created_at')
        return {
            'data': Paginator(object_list, per_page).page(page).object_list,
            'meta': {
                'page': page,
                'per_page': per_page,
                'total': object_list.count()
            }
        }

    def create_email(self, **kwargs):
        (email, errors) = (self.model(), {})
        errors['body'] = error_messages.REQUIRED.format('email body is ') if not kwargs.get('body') else None

        if not kwargs.get('recipients') or not isinstance(kwargs.get('recipients'), list) or\
                (isinstance(kwargs.get('recipients'), list) and len(kwargs.get('recipients')) == 0):
            errors['recipients'] = error_messages.REQUIRED.format('email recipients are ')

        if len(remove_dict_none_values(errors)) != 0:
            raise ValidationError(str(errors))

        email.recipients = kwargs.get('recipients')
        email.body = kwargs.get('body')

        email.save(using=self._db)
        send_mail('BitLipa', '', settings.EMAIL_SENDER, kwargs.get('recipients'), False, html_message=email.body)
        return email

    def get_email(self, **kwargs):
        try:
            email = self.model.objects.get(**kwargs)
            return email
        except self.model.DoesNotExist:
            return self.model(amount=to_decimal(0))

    def remove(self, id=None):
        email = self.model.objects.get(id=id)
        email.delete()
        return email
