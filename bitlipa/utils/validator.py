from typing import Tuple
from django.core import validators
from django.core import exceptions as core_exceptions

from bitlipa.resources import error_messages


class Validator:
    def validate_phonenumber(phonenumber) -> Tuple[str, core_exceptions.ValidationError]:
        phone_regex = validators.RegexValidator(regex=r'^\+?1?\d{9,15}$', message=error_messages.WRONG_PHONE_NUMBER)
        phone_regex(phonenumber)
        return phonenumber

    def validate_email(email) -> Tuple[str, core_exceptions.ValidationError]:
        try:
            validators.validate_email(email)
            return email
        except core_exceptions.ValidationError:
            raise core_exceptions.ValidationError(error_messages.WRONG_EMAIL)
