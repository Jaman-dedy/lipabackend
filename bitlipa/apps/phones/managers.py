from django.db import models
from bitlipa.resources import error_messages
import datetime
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError, PermissionDenied


class PhoneManager(models.Manager):
    def create_phone(self, user, **kwargs):
        phone = self.model()

        if not kwargs.get('phonenumber'):
            raise ValidationError(error_messages.REQUIRED.format(' phonenumber is '))
        if not kwargs.get('email'):
            raise ValidationError(error_messages.REQUIRED.format(' email is '))
        phonenumber = kwargs.get('phonenumber')
        if user.phonenumber == phonenumber:
                    raise PermissionDenied(error_messages.PHONE_NUMBER_EXIST.format(f' {phonenumber} '))

        
        phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message=error_messages.WRONG_PHONE_NUMBER)
        phone_regex(kwargs.get('phonenumber'))
        phone.phonenumber = kwargs.get('phonenumber')
        phone.email = kwargs.get('email')

        phone.save(using=self._db)
        phone.user = user
        return phone

    def update(self, id=None, **kwargs):
        phone = self.model.objects.get(id=id)
        phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message=error_messages.WRONG_PHONE_NUMBER)
        phone_regex(kwargs.get('phonenumber'))
        phone.phonenumber = kwargs.get('phonenumber') or phone.phonenumber
        phone.email = kwargs.get('email') or phone.email

        phone.save(using=self._db)
        return phone

    def delete(self, id=None, **kwargs):
        phone = self.model.objects.get(id=id)

        phone.deleted_at = datetime.datetime.now()

        phone.save(using=self._db)
        return phone
