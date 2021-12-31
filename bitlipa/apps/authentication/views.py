from django.conf import settings
from contextlib import suppress
from django.db.utils import IntegrityError
from rest_framework import viewsets, status
from rest_framework.decorators import action
from django.core.mail import send_mail
from django.template import loader
from rest_framework import exceptions as drf_exceptions
from django.core import exceptions as core_exceptions

from bitlipa.resources import success_messages
from bitlipa.utils.jwt_util import JWTUtil
from bitlipa.apps.fiat_wallets.models import FiatWallet
from bitlipa.apps.fiat_wallets.serializers import FiatWalletSerializer
from bitlipa.apps.users.models import User
from bitlipa.apps.users.serializers import UserSerializer
from bitlipa.resources import error_messages
from bitlipa.utils.get_http_error_message_and_code import get_http_error_message_and_code
from bitlipa.utils.http_response import http_response
from bitlipa.utils.get_object_attr import get_object_attr
from bitlipa.utils.auth_util import AuthUtil
from bitlipa.utils.validator import Validator


class AuthViewSet(viewsets.ViewSet):
    """
    Authentication endpoints.
    """

    @action(methods=['post'], detail=False, url_path='send-email-verification-link', url_name='send_email_link')
    def send_email_link(self, request):
        if not request.data.get('email'):
            raise core_exceptions.ValidationError(error_messages.REQUIRED.format('Email is '))

        email = Validator.validate_email(request.data.get('email'))
        with suppress(User.DoesNotExist):
            user = User.objects.get(email__iexact=email)
            if user.is_email_verified and user.is_phone_verified and user.phonenumber and user.pin:
                raise IntegrityError(error_messages.CONFLICT.format(f'{email} '))
            elif not user.phonenumber or not user.pin:
                user.delete()

        email_token = JWTUtil.encode({"email": email, "from_email": True}, exp_hours=24)
        link = f'{request.data.get("redirect_link") or settings.API_URL}/auth/verify-email/{email_token}/'
        content = loader.render_to_string('verify_email.html', {
            'link': link
        })
        send_mail('Verify account', '', settings.EMAIL_SENDER, [email], False, html_message=content)
        return http_response(status=status.HTTP_201_CREATED, message=success_messages.EMAIL_SENT, data={
            "token": JWTUtil.encode({"email": email}, exp_hours=24),
            "email_token": email_token if settings.DEBUG else None
        })

    @action(methods=['get'], detail=False, url_path=r'verify-email/(?P<token>.*)', url_name='verify_email')
    def verify_email(self, request, *args, **kwargs):
        try:
            decoded_token = JWTUtil.decode(kwargs.get('token'))
            if decoded_token.get('from_email') is not True:
                raise drf_exceptions.PermissionDenied(error_messages.WRONG_TOKEN)

            with suppress(User.DoesNotExist):
                User.objects.save_email(**decoded_token)

            content = loader.render_to_string('email_verified.html', {
                'link': settings.MOBILE_APP_URL.replace(
                    '/#Intent', f'?emailVerified=true&&email={decoded_token.get("email")}&&token={kwargs.get("token")}/#Intent'),
                'email': decoded_token.get('email')
            })
            return http_response(status=status.HTTP_200_OK, message=success_messages.SUCCESS, html=content)
        except Exception as e:
            content = loader.render_to_string('email_verified.html', {
                'link': settings.MOBILE_APP_URL.replace('/#Intent', '?emailVerified=false/#Intent'),
                'error': get_http_error_message_and_code(e).get('message')
            })
            return http_response(status=status.HTTP_200_OK, message=success_messages.SUCCESS, html=content)

    @action(methods=['put'], detail=False, url_path='verify-phonenumber', url_name='verify_phonenumber')
    def verify_phonenumber(self, request):
        AuthUtil.is_auth(request)
        user = User.objects.save_or_verify_phonenumber(email=request.decoded_token.get('email'), **request.data)
        serializer = UserSerializer(user)
        return http_response(status=status.HTTP_200_OK, message=success_messages.SUCCESS, data=serializer.data)

    @action(methods=['post'], detail=False, url_path='signup', url_name='signup')
    def create_user(self, request):
        serializer = UserSerializer(User.objects.create(**request.data))

        return http_response(status=status.HTTP_201_CREATED, data=serializer.data)

    @action(methods=['post'], detail=False, url_path='create-admin', url_name='create-admin')
    def create_admin(self, request):
        AuthUtil.is_auth(request, is_admin=True)
        serializer = UserSerializer(User.objects.create_admin(creator=request.user, **request.data))

        return http_response(status=status.HTTP_201_CREATED, data=serializer.data)

    @action(methods=['post'], detail=False, url_path='login', url_name='login')
    def login_user(self, request):
        user = User.objects.login(**request.data)
        if get_object_attr(user, 'is_account_blocked'):
            return http_response(status=status.HTTP_403_FORBIDDEN,
                                 message=error_messages.ACCOUNT_LOCKED_DUE_TO_SUSPICIOUS_ACTIVITIES)
        if get_object_attr(user, 'otp'):
            content = loader.render_to_string('confirm_login.html', {'verification_code': user.otp})
            send_mail('Confirm login', '', settings.EMAIL_SENDER, [user.email], False, html_message=content)
            return http_response(status=status.HTTP_401_UNAUTHORIZED, data={
                "is_otp_required": True,
                "message": success_messages.CONFIRM_LOGIN
            })
        serializer = UserSerializer(user, context={'include_wallets': True, 'request': request})
        user_token = JWTUtil.encode({"email": user.email, "phonenumber": user.phonenumber}, exp_hours=24)

        if not len(serializer.data.get('fiat_wallets')):
            fiat_wallet = FiatWallet.create_default(FiatWallet, user)
            if fiat_wallet and isinstance(fiat_wallet, FiatWallet):
                return http_response(status=status.HTTP_200_OK, data={
                    "user": {**serializer.data, 'fiat_wallets': [FiatWalletSerializer(fiat_wallet).data]},
                    "token": user_token
                })

        return http_response(status=status.HTTP_200_OK, data={"user": serializer.data, "token": user_token})

    @action(methods=['post'], detail=False, url_path='admin/login', url_name='admin/login')
    def login_admin(self, request):
        user = User.objects.login_admin(**request.data)

        if user.is_account_blocked:
            return http_response(status=status.HTTP_403_FORBIDDEN,
                                 message=error_messages.ACCOUNT_LOCKED_DUE_TO_SUSPICIOUS_ACTIVITIES)

        serializer = UserSerializer(user)
        user_token = JWTUtil.encode({"email": user.email, "phonenumber": user.phonenumber}, exp_hours=24)
        return http_response(status=status.HTTP_200_OK, data={"user": serializer.data, "token": user_token})

    @action(methods=['get'], detail=False, url_path=r'refresh-token/(?P<token>.*)', url_name='refresh_token')
    def refresh_token(self, request, *args, **kwargs):
        decoded_token = JWTUtil.decode(kwargs.get('token'), options={"verify_exp": False})
        decoded_token.pop('exp', None)
        return http_response(status=status.HTTP_200_OK, data={"token": JWTUtil.encode(decoded_token)})

    def send_reset_pin_or_password_link(self, field_to_reset, request):
        if not request.data.get('email'):
            raise core_exceptions.ValidationError(error_messages.REQUIRED.format('Email is '))

        email = Validator.validate_email(request.data.get('email'))
        user = User.objects.get(email__iexact=email)

        if user.is_account_blocked:
            return http_response(status=status.HTTP_403_FORBIDDEN,
                                 message=error_messages.ACCOUNT_LOCKED_DUE_TO_SUSPICIOUS_ACTIVITIES)

        email_token = JWTUtil.encode({
            'email': user.email, 'from_email': True, 'field_to_reset': field_to_reset
        }, exp_hours=24)
        link = f'{request.data.get("redirect_link") or settings.API_URL}/auth/reset-{field_to_reset.lower()}/{email_token}/'
        content = loader.render_to_string(f'reset_{field_to_reset.lower()}.html', {'link': link, 'field_to_reset': field_to_reset})

        send_mail(f'Reset {field_to_reset}', '', settings.EMAIL_SENDER, [user.email], False, html_message=content)

        return http_response(status=status.HTTP_201_CREATED, message=success_messages.EMAIL_SENT, data={
            'link': link,
            "token": JWTUtil.encode({"email": user.email}, exp_hours=24),
            **({'email_token': email_token} if settings.DEBUG else {})
        })

    @action(methods=['post'], detail=False, url_path='send-reset-pin-link', url_name='send_reset-pin_link')
    def send_reset_pin_link(self, request):
        return AuthViewSet.send_reset_pin_or_password_link(self, 'PIN', request)

    @action(methods=['post'], detail=False, url_path='send-reset-password-link', url_name='send_reset-password_link')
    def send_reset_password_link(self, request):
        return AuthViewSet.send_reset_pin_or_password_link(self, 'password', request)

    def reset_pin_or_password(self, field_to_reset, request, **kwargs):
        decoded_token = JWTUtil.decode(kwargs.get('token'))
        if not (decoded_token.get('from_email') is True and decoded_token.get('field_to_reset') == field_to_reset):
            raise drf_exceptions.PermissionDenied(error_messages.WRONG_TOKEN)

        data = {**request.data, 'field_to_reset': field_to_reset, 'email': decoded_token.get('email')}
        user = User.objects.reset_pin_or_password(**data)

        if user.is_account_blocked:
            return http_response(status=status.HTTP_403_FORBIDDEN,
                                 message=error_messages.ACCOUNT_LOCKED_DUE_TO_SUSPICIOUS_ACTIVITIES)

        return http_response(status=status.HTTP_200_OK,
                             message=success_messages.RESET_SUCCESS.format(f'{field_to_reset} '))

    @action(methods=['put', 'get'], detail=False, url_path=r'reset-pin/(?P<token>.*)', url_name='reset_pin')
    def reset_pin(self, request, *args, **kwargs):
        field_to_reset = 'PIN'

        if request.method == 'PUT':
            return AuthViewSet.reset_pin_or_password(self, field_to_reset, request, **kwargs)

        if request.method == 'GET':
            content = loader.render_to_string('reset_pin_or_password.html', {
                'field_to_reset': field_to_reset,
                'link': settings.MOBILE_APP_URL.replace(
                    '/#Intent', f'?reset={field_to_reset}&token={kwargs.get("token")}/#Intent')})
            return http_response(status=status.HTTP_200_OK, message=success_messages.SUCCESS, html=content)

    @action(methods=['put', 'get'], detail=False, url_path=r'reset-password/(?P<token>.*)', url_name='reset_password')
    def reset_password(self, request, *args, **kwargs):
        field_to_reset = 'password'

        if request.method == 'PUT':
            return AuthViewSet.reset_pin_or_password(self, field_to_reset, request, **kwargs)

        if request.method == 'GET':
            content = loader.render_to_string('reset_pin_or_password.html', {
                'field_to_reset': field_to_reset,
                'link': settings.MOBILE_APP_URL.replace(
                    '/#Intent', f'?reset={field_to_reset}&token={kwargs.get("token")}/#Intent')})
            return http_response(status=status.HTTP_200_OK, message=success_messages.SUCCESS, html=content)

    @action(methods=['put'], detail=False, url_path='change-pin', url_name='change_pin')
    def change_pin(self, request):
        AuthUtil.is_auth(request)
        User.objects.change_pin(user=request.user, **request.data)
        return http_response(status=status.HTTP_200_OK, message="PIN changed successfully")
