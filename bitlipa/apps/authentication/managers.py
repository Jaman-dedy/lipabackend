from contextlib import suppress
from datetime import datetime, timezone
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError, PermissionDenied
from django.core.validators import RegexValidator
import moneyed

from bitlipa.resources.constants import MAX_PIN_CHANGE_COUNT, MAX_PIN_CHANGE_DAYS_INTERVAL
from bitlipa.resources import error_messages
from bitlipa.utils.get_object_attr import get_object_attr
from bitlipa.utils.send_sms import send_sms
from bitlipa.utils.remove_dict_none_values import remove_dict_none_values
from bitlipa.utils.validator import Validator
from bitlipa.apps.otp.models import OTP
from bitlipa.apps.global_configs.models import GlobalConfig


class AuthManager:
    def save_email(self, **kwargs):
        email = kwargs.get('email')

        if not email:
            raise ValidationError(error_messages.REQUIRED.format('Email is '))

        try:
            user = self.model.objects.get(email=email)
        except self.model.DoesNotExist:
            user = self.model()

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
            otp_obj = OTP.objects.find(
                otp=kwargs.get('OTP'), email=email, phonenumber=kwargs.get('phonenumber'), destination=OTP.OTPDestinations.SMS)
            user.phonenumber = kwargs.get('phonenumber')
            user.is_phone_verified = True
            user.save(using=self._db)
            OTP.objects.remove_all(email=email, phonenumber=kwargs.get('phonenumber'), destination=OTP.OTPDestinations.SMS)
            return user

        otp_obj = OTP.objects.save(email=email, phonenumber=kwargs.get('phonenumber'), digits=4)
        message = f'<#> Your {settings.APP_NAME} verification code is: {otp_obj.otp}\n {settings.MOBILE_APP_HASH}'
        send_sms(otp_obj.phonenumber, message=message)
        return user

    def create_user(self, creator, **kwargs):
        user = self.model()

        if not kwargs.get('email'):
            raise ValidationError(error_messages.REQUIRED.format('Email is '))
        if not kwargs.get('phonenumber'):
            raise ValidationError(error_messages.REQUIRED.format('Phone number is '))
        if not kwargs.get('PIN'):
            raise ValidationError(error_messages.REQUIRED.format('PIN is '))

        phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message=error_messages.WRONG_PHONE_NUMBER)
        phone_regex(kwargs.get('phonenumber'))
        user.email = self.normalize_email(kwargs.get('email'))
        user.phonenumber = kwargs.get('phonenumber')
        user.first_name = kwargs.get('first_name')
        user.middle_name = kwargs.get('middle_name')
        user.last_name = kwargs.get('last_name')
        user.pin = make_password(kwargs.get('PIN'))
        user.creator_id = get_object_attr(creator, 'id')

        if kwargs.get('password'):
            user.password = make_password(kwargs.get('password'))

        user.is_phone_verified = True
        user.is_email_verified = True
        user.save(using=self._db)
        return user

    def create_admin(self, creator, **kwargs):
        user = self.model()

        if not kwargs.get('email'):
            raise ValidationError(error_messages.REQUIRED.format('Email is '))

        if not kwargs.get('phonenumber'):
            raise ValidationError(error_messages.REQUIRED.format('Phone number is '))

        user.email = self.normalize_email(kwargs.get('email'))
        phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message=error_messages.WRONG_PHONE_NUMBER)
        phone_regex(kwargs.get('phonenumber'))
        user.phonenumber = kwargs.get('phonenumber')

        user.first_name = kwargs.get('first_name')
        user.middle_name = kwargs.get('middle_name')
        user.last_name = kwargs.get('last_name')
        user.creator_id = creator.id

        if kwargs.get('password'):
            user.password = make_password(kwargs.get('password'))

        user.is_phone_verified = True
        user.is_password_temporary = True
        user.status = 'Active'
        user.is_admin = True
        user.save(using=self._db)
        return user

    def check_login_device(user, **kwargs):
        if user.device_id and not kwargs.get('OTP') and kwargs.get('device_id') != user.device_id:
            return OTP.objects.save(email=user.email,
                                    phonenumber=user.phonenumber,
                                    digits=4,
                                    destination=OTP.OTPDestinations.EMAIL)

        # check if OTP exists otherwise throw an exception
        if user.device_id and kwargs.get('OTP') and kwargs.get('device_id') != user.device_id:
            OTP.objects.find(otp=kwargs.get('OTP'),
                             email=user.email,
                             phonenumber=user.phonenumber,
                             destination=OTP.OTPDestinations.EMAIL)

    def check_login_country(user, **kwargs):
        new_country = kwargs.get('country')
        if new_country and user.country and not kwargs.get('OTP') and str(new_country).lower() != user.country.lower():
            return OTP.objects.save(email=user.email,
                                    phonenumber=user.phonenumber,
                                    digits=4,
                                    destination=OTP.OTPDestinations.EMAIL)

        # check if OTP exists otherwise throw an exception
        if new_country and user.country and kwargs.get('OTP') and str(new_country).lower() != user.country.lower():
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

        try:
            user = self.model.objects.get(email=self.normalize_email(kwargs.get('email')))
        except self.model.DoesNotExist:
            raise PermissionDenied(error_messages.WRONG_CREDENTAILS)

        if user.is_account_blocked:
            raise PermissionDenied(error_messages.ACCOUNT_LOCKED_DUE_TO_SUSPICIOUS_ACTIVITIES)

        if user.is_email_verified is False or user.is_phone_verified is False:
            errors['email'] = error_messages.EMAIL_NOT_VERIFIED if user.is_email_verified is False else None
            errors['phonenumber'] = error_messages.PHONE_NOT_VERIFIED if user.is_phone_verified is False else None
            raise PermissionDenied(str(remove_dict_none_values(errors)))

        with suppress(GlobalConfig.DoesNotExist):
            max_wrong_login_attempts = GlobalConfig.objects.get(name__iexact='max wrong login attempts')
            if user.wrong_login_attempts_count >= max_wrong_login_attempts.data:
                date_diff = datetime.now(timezone.utc) - user.last_wrong_login_attempt_date
                if date_diff.days < 1:
                    raise PermissionDenied(error_messages.ACCOUNT_LOCKED_DUE_WRONG_LOGIN_ATTEMPTS)
                else:
                    user.last_wrong_login_attempt_date = None
                    user.wrong_login_attempts_count = 0

        if not check_password(kwargs.get("PIN"), user.pin):
            user.last_wrong_login_attempt_date = datetime.now()
            user.wrong_login_attempts_count += 1
            user.save(using=self._db)
            raise PermissionDenied(error_messages.WRONG_CREDENTAILS)

        otp_obj = AuthManager.check_login_device(user, **kwargs) or AuthManager.check_login_country(user, **kwargs)
        if otp_obj:
            return otp_obj

        user.device_id = kwargs.get('device_id') or user.device_id
        user.country = kwargs.get('country') or user.country
        user.country_code = kwargs.get('country_code') or user.country_code
        user.local_currency = kwargs.get('local_currency') or user.local_currency
        user.firebase_token = kwargs.get('firebase_token') or user.firebase_token
        user.last_wrong_login_attempt_date = None
        user.wrong_login_attempts_count = 0

        if not user.local_currency and user.country_code:
            with suppress(Exception):
                user.local_currency = moneyed.get_currencies_of_country(user.country_code)[0]

        user.save(using=self._db)
        OTP.objects.remove_all(email=user.email, phonenumber=user.phonenumber, destination=OTP.OTPDestinations.EMAIL)
        return user

    def login_admin(self, **kwargs):
        errors = {}
        errors['email'] = error_messages.REQUIRED.format('Email is ') if not kwargs.get('email') else None
        errors['password'] = error_messages.REQUIRED.format('password is ') if not kwargs.get('password') else None

        if len(remove_dict_none_values(errors)) != 0:
            raise ValidationError(str(errors))

        user = self.model.objects.get(email=self.normalize_email(kwargs.get('email')))

        if user.is_email_verified is False or user.is_phone_verified is False or user.is_admin is False:
            errors['email'] = error_messages.EMAIL_NOT_VERIFIED if user.is_email_verified is False else None
            errors['phonenumber'] = error_messages.PHONE_NOT_VERIFIED if user.is_phone_verified is False else None
            errors['is_admin'] = error_messages.ACCESS_DENIED if user.is_admin is False else None
            raise PermissionDenied(str(remove_dict_none_values(errors)))

        if not check_password(kwargs.get("password"), user.password):
            raise PermissionDenied(error_messages.WRONG_CREDENTAILS)
        return user

    def reset_pin_or_password(self, **kwargs):
        field_to_reset = kwargs.get('field_to_reset')

        if field_to_reset not in ['PIN', 'password']:
            raise ValidationError(error_messages.REQUIRED.format('PIN or password is '))

        errors = {}
        errors['email'] = error_messages.REQUIRED.format('Email is ') if not kwargs.get('email') else None
        errors[field_to_reset] = error_messages.REQUIRED.format(f'{field_to_reset} is ') \
            if not kwargs.get(field_to_reset) else None

        if len(remove_dict_none_values(errors)) != 0:
            raise ValidationError(str(errors))

        user = self.model.objects.get(email=self.normalize_email(kwargs.get('email')))

        if user.is_account_blocked:
            return user

        if field_to_reset == 'PIN' and user.pin_change_count == MAX_PIN_CHANGE_COUNT and user.initial_pin_change_date:
            date_diff = datetime.now(timezone.utc) - user.initial_pin_change_date
            if date_diff.days <= MAX_PIN_CHANGE_DAYS_INTERVAL:
                user.is_account_blocked = True
                user.save(using=self._db)
                return user
            else:
                user.pin_change_count = 0
                user.initial_pin_change_date = datetime.now()

        if field_to_reset == 'PIN' and user.pin_change_count < MAX_PIN_CHANGE_COUNT:
            user.pin_change_count += 1
            user.initial_pin_change_date = user.initial_pin_change_date or datetime.now()

        if kwargs.get('is_password_temporary') is False:
            user.is_password_temporary = False

        setattr(user, field_to_reset.lower(), make_password(kwargs.get(field_to_reset)))
        user.save(using=self._db)
        return user

    def change_pin(self, user, **kwargs):
        errors = {}
        errors['current_PIN'] = error_messages.REQUIRED.format('current PIN is ') if not kwargs.get('current_PIN') else None
        errors['new_PIN'] = error_messages.REQUIRED.format('new PIN is ') if not kwargs.get('new_PIN') else None

        if len(remove_dict_none_values(errors)) != 0:
            raise ValidationError(str(errors))

        if not check_password(kwargs.get("current_PIN"), user.pin):
            raise PermissionDenied(error_messages.WRONG_PIN)

        user.pin = make_password(kwargs.get('new_PIN'))
        user.save(using=self._db)
        return user
