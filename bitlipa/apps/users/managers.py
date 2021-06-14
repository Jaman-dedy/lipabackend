from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.core.validators import RegexValidator


from bitlipa.resources import error_messages


class UserManager(BaseUserManager):
    def save_email(self, **kwargs):
        user = self.model()

        if not kwargs.get('email'):
            raise ValueError(error_messages.REQUIRED.format('Email is '))

        user.email = self.normalize_email(kwargs.get('email'))
        user.is_email_verified = True
        user.save(using=self._db)
        return user

    def create(self, **kwargs):
        user = self.model()

        if not kwargs.get('email'):
            raise ValueError(error_messages.REQUIRED.format('Email is '))

        if not kwargs.get('phonenumber'):
            raise ValueError(error_messages.REQUIRED.format('Phone number is '))

        if not kwargs.get('PIN'):
            raise ValueError(error_messages.REQUIRED.format('PIN is '))

        user.email = self.normalize_email(kwargs.get('email'))
        phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message=error_messages.WRONG_PHONE_NUMBER)
        phone_regex(kwargs.get('phonenumber'))
        user.phonenumber = kwargs.get('phonenumber')

        user.first_name = kwargs.get('first_name')
        user.middle_name = kwargs.get('middle_name')
        user.last_name = kwargs.get('last_name')
        user.pin = make_password(kwargs.get('PIN'))

        if kwargs.get('password'):
            user.password = make_password(kwargs.get('password'))

        user.save(using=self._db)
        return user

    def update(self, id=None, email=None, **kwargs):
        user = self.model.objects.get(email=email) if email else self.model.objects.get(id=id)

        # TODO: add OTP verification
        if kwargs.get('phonenumber'):
            phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message=error_messages.WRONG_PHONE_NUMBER)
            phone_regex(kwargs.get('phonenumber'))
            user.phonenumber = kwargs.get('phonenumber')

        user.first_name = kwargs.get('first_name') or user.first_name
        user.middle_name = kwargs.get('middle_name') or user.middle_name
        user.last_name = kwargs.get('last_name') or user.last_name

        if not user.pin and kwargs.get('PIN'):
            user.pin = make_password(kwargs.get('PIN'))

        if not user.password and kwargs.get('password'):
            user.password = make_password(kwargs.get('password'))

        user.save(using=self._db)
        return user
