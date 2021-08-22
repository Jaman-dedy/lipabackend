from django.conf import settings
from django.contrib.auth.models import BaseUserManager
from django.core.paginator import Paginator
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError, PermissionDenied
from django.core.validators import RegexValidator
from django.db import models

from bitlipa.resources import constants
from bitlipa.resources import error_messages
from bitlipa.utils.to_int import to_int
from bitlipa.utils.list_utils import filter_list
from bitlipa.utils.validator import Validator
from bitlipa.apps.otp.models import OTP
from bitlipa.utils.send_sms import send_sms
from bitlipa.utils.remove_dict_none_values import remove_dict_none_values


class UserManager(BaseUserManager):
    def list(self, user=None, **kwargs):
        table_fields = {}
        (page, per_page) = (to_int(kwargs.get('page'), 1), to_int(kwargs.get('per_page'), constants.DB_ITEMS_LIMIT))

        for key in filter_list(kwargs.keys(), values_to_exclude=['page', 'per_page']):
            if kwargs[key] is not None:
                table_fields[key] = kwargs[key]

        query = models.Q(**{'deleted_at': None, **table_fields})

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

    def save_email(self, **kwargs):
        user = self.model()

        if not kwargs.get('email'):
            raise ValidationError(error_messages.REQUIRED.format('Email is '))

        user.email = self.normalize_email(kwargs.get('email'))
        user.is_email_verified = True
        user.save(using=self._db)
        return user

    def save_or_verify_phonenumber(self, id=None, email=None, **kwargs):
        user = self.model.objects.get(email=email) if email else self.model.objects.get(id=id)

        if not email:
            raise ValidationError(error_messages.REQUIRED.format('Email is '))

        if kwargs.get('phonenumber') == user.phonenumber:
            return user

        Validator.validate_phonenumber(kwargs.get('phonenumber'))

        if kwargs.get('OTP'):
            otp_obj = OTP.objects.find(otp=kwargs.get('OTP'), email=email, phonenumber=kwargs.get('phonenumber'))
            user.phonenumber = kwargs.get('phonenumber')
            user.is_phone_verified = True
            user.save(using=self._db)
            OTP.objects.remove_all(email=email, phonenumber=kwargs.get('phonenumber'), destination=OTP.OTPDestinations.SMS)
            return user

        otp_obj = OTP.objects.save(email=email, phonenumber=kwargs.get('phonenumber'), digits=4)
        message = f'<#> Your {settings.APP_NAME} verification code is: {otp_obj.otp}\n {settings.MOBILE_APP_HASH}'
        send_sms(otp_obj.phonenumber, message=message)
        return user

    def create(self, **kwargs):
        user = self.model()

        if not kwargs.get('email'):
            raise ValidationError(error_messages.REQUIRED.format('Email is '))

        if not kwargs.get('phonenumber'):
            raise ValidationError(error_messages.REQUIRED.format('Phone number is '))

        if not kwargs.get('PIN'):
            raise ValidationError(error_messages.REQUIRED.format('PIN is '))

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

        user.is_phone_verified = True
        user.save(using=self._db)
        return user

    def update(self, id=None, email=None, **kwargs):
        user = self.model.objects.get(email=email) if email else self.model.objects.get(id=id)

        user.first_name = kwargs.get('first_name', user.first_name)
        user.middle_name = kwargs.get('middle_name', user.middle_name)
        user.last_name = kwargs.get('last_name', user.last_name)
        user.firebase_token = kwargs.get('firebase_token', user.firebase_token)
        user.country = kwargs.get('country', user.country)
        user.country_code = kwargs.get('country_code', user.country_code)

        if not user.pin and kwargs.get('PIN'):
            user.pin = make_password(kwargs.get('PIN'))

        if not user.password and kwargs.get('password'):
            user.password = make_password(kwargs.get('password'))

        if not user.phonenumber and kwargs.get('phonenumber'):
            phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message=error_messages.WRONG_PHONE_NUMBER)
            phone_regex(kwargs.get('phonenumber'))
            user.phonenumber = kwargs.get('phonenumber')

        user.save(using=self._db)
        return user

    def check_login_from_different_device(user, **kwargs):
        if user.device_id and not kwargs.get('OTP') and kwargs.get('device_id') != user.device_id:
            return OTP.objects.save(email=user.email,
                                    phonenumber=user.phonenumber,
                                    digits=4,
                                    destination=OTP.OTPDestinations.EMAIL)

        if user.device_id and kwargs.get('OTP') and kwargs.get('device_id') != user.device_id:
            OTP.objects.find(otp=kwargs.get('OTP'),
                             email=user.email,
                             phonenumber=user.phonenumber,
                             destination=OTP.OTPDestinations.EMAIL)

    def check_login_from_different_country(user, **kwargs):
        if user.country and not kwargs.get('OTP') and kwargs.get('country', '').lower() != user.country.lower():
            return OTP.objects.save(email=user.email,
                                    phonenumber=user.phonenumber,
                                    digits=4,
                                    destination=OTP.OTPDestinations.EMAIL)

        if user.country and kwargs.get('OTP') and kwargs.get('country', '').lower() != user.country.lower():
            OTP.objects.find(otp=kwargs.get('OTP'),
                             email=user.email,
                             phonenumber=user.phonenumber,
                             destination=OTP.OTPDestinations.EMAIL)

    def login(self, **kwargs):
        errors = {}
        errors['email'] = error_messages.REQUIRED.format('Email is ') if not kwargs.get('email') else None
        errors['PIN'] = error_messages.REQUIRED.format('PIN is ') if not kwargs.get('PIN') else None
        errors['device_id'] = error_messages.REQUIRED.format('Device id is ') if not kwargs.get('device_id') else None

        if len(remove_dict_none_values(errors)) != 0:
            raise ValidationError(str(errors))

        user = self.model.objects.get(email=self.normalize_email(kwargs.get('email')))
        otp_obj = UserManager.check_login_from_different_device(user, **kwargs)
        otp_obj = UserManager.check_login_from_different_country(user, **kwargs) or otp_obj

        if otp_obj:
            return otp_obj

        OTP.objects.remove_all(email=user.email, phonenumber=user.phonenumber, destination=OTP.OTPDestinations.EMAIL)

        user.device_id = kwargs.get('device_id')
        user.country = kwargs.get('country')
        user.save(using=self._db)

        if user.is_email_verified is False or user.is_phone_verified is False:
            errors['email'] = error_messages.EMAIL_NOT_VERIFIED if user.is_email_verified is False else None
            errors['phonenumber'] = error_messages.PHONE_NOT_VERIFIED if user.is_phone_verified is False else None
            raise PermissionDenied(str(remove_dict_none_values(errors)))

        if not check_password(kwargs.get("PIN"), user.pin):
            raise PermissionDenied(error_messages.WRONG_CREDENTAILS)
        return user
