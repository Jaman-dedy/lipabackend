from django.contrib.auth.models import BaseUserManager
from django.core.paginator import Paginator
from django.contrib.auth.hashers import make_password
from django.core.validators import RegexValidator
from django.db import models

from bitlipa.apps.authentication.managers import AuthManager
from bitlipa.resources import constants
from bitlipa.resources import error_messages
from bitlipa.utils.to_int import to_int
from bitlipa.utils.remove_dict_none_values import remove_dict_none_values


class UserManager(BaseUserManager, AuthManager):
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

    def list_admins(self, **kwargs):
        table_fields = {**kwargs}
        page = to_int(kwargs.get('page'), 1)
        per_page = to_int(kwargs.get('per_page'), constants.DB_ITEMS_LIMIT)

        for key in ['page', 'per_page']:
            table_fields.pop(key, None)  # remove fields not in the DB table

        query = models.Q(**{'deleted_at': None, **remove_dict_none_values(table_fields)})

        object_list = self.model.objects.filter(is_admin=True)
        data = Paginator(object_list, per_page).page(page).object_list
        return {
            'data': data,
            'meta': {
                'page': page,
                'per_page': per_page,
                'total': object_list.count()
            }
        }

    def update(self, id=None, email=None, **kwargs):
        user = self.model.objects.get(email=email) if email else self.model.objects.get(id=id)

        user.first_name = kwargs.get('first_name', user.first_name)
        user.middle_name = kwargs.get('middle_name', user.middle_name)
        user.last_name = kwargs.get('last_name', user.last_name)
        user.firebase_token = kwargs.get('firebase_token', user.firebase_token)
        user.country = kwargs.get('country', user.country)
        user.country_code = kwargs.get('country_code', user.country_code)
        user.local_currency = kwargs.get('local_currency', user.local_currency)
        user.picture_url = kwargs.get('picture_url', user.picture_url)
        user.document_type = kwargs.get('document_type', user.document_type)
        user.document_front_url = kwargs.get('document_front_url', user.document_front_url)
        user.document_back_url = kwargs.get('document_back_url', user.document_back_url)
        user.selfie_picture_url = kwargs.get('selfie_picture_url', user.selfie_picture_url)
        user.proof_of_residence_url = kwargs.get('proof_of_residence_url', user.proof_of_residence_url)
        user.is_account_verified = kwargs.get('is_account_verified', user.is_account_verified)
        user.status = kwargs.get('status', user.status)

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
