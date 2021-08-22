from django.db import models
from django.core.exceptions import ValidationError


from bitlipa.resources import error_messages
from bitlipa.utils.otp_util import OTPUtil
from bitlipa.utils.validator import Validator


class OTPManager(models.Manager):
    def save(self, otp=None, email=None, phonenumber=None, digits=None, destination=None):
        otp_obj = self.model()

        if not email or not phonenumber:
            raise ValidationError(error_messages.REQUIRED.format('Email is ')) \
                if not email else \
                ValidationError(error_messages.REQUIRED.format('Phone number is '))

        if email:
            otp_obj.email = email

        if phonenumber:
            Validator.validate_phonenumber(phonenumber)
            otp_obj.phonenumber = phonenumber

        if destination:
            otp_obj.destination = destination

        otp_obj.otp = otp or OTPUtil.generate(digits=digits)
        otp_obj.save(using=self._db)
        return otp_obj

    def find(self, otp=None, email=None, phonenumber=None, destination=None):
        try:
            return self.model.objects.get(email=email, otp=otp, destination=destination) \
                if email else \
                self.model.objects.get(phonenumber=phonenumber, otp=otp, destination=destination)
        except Exception:
            raise ValidationError(error_messages.WRONG_OTP)

    def remove(self, otp=None, email=None, phonenumber=None):
        try:
            if otp and email and phonenumber:
                self.model.objects.get(email=email, phonenumber=phonenumber, otp=otp).delete()
            else:
                self.model.objects.get(email=email, otp=otp).delete() \
                    if email else \
                    self.model.objects.get(phonenumber=phonenumber, otp=otp).delete()
        except Exception:
            return None

    def remove_all(self, email=None, phonenumber=None, destination=None):
        try:
            if email and phonenumber:
                self.model.objects.filter(email=email, phonenumber=phonenumber, destination=destination).delete()
            else:
                self.model.objects.filter(email=email).delete() \
                    if email else \
                    self.model.objects.filter(phonenumber=phonenumber, destination=destination).delete()
        except Exception:
            return None
