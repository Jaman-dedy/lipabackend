from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from django.core.mail import send_mail
from django.template import loader
from rest_framework import exceptions as drf_exceptions
from django.core import exceptions as core_exceptions

from bitlipa.resources import success_messages
from bitlipa.utils.jwt_util import JWTUtil
from bitlipa.apps.users.models import User
from bitlipa.apps.users.serializers import UserSerializer
from bitlipa.resources import error_messages
from bitlipa.utils.http_response import http_response
from bitlipa.utils.send_sms import send_sms
from bitlipa.utils.auth_util import AuthUtil
from bitlipa.utils.validator import Validator


class AuthViewSet(viewsets.ViewSet):
    """
    API endpoint that allows users to be registered/login.
    """

    @action(methods=['post'], detail=False, url_path='send-email-verification-link', url_name='send_email_verification_link')
    def send_email_verification_link(self, request):
        if not request.data.get('email'):
            raise core_exceptions.ValidationError(error_messages.REQUIRED.format('Email is '))

        email = Validator.validate_email(request.data.get('email'))
        email_token = JWTUtil.encode({"email": email, "from_email": True}, expiration_hours=24)
        content = loader.render_to_string('verify_email.html', {'verification_link': f'{settings.API_URL}/auth/verify-email/{email_token}/'})
        send_mail('Verify account', '', settings.EMAIL_SENDER, [email], fail_silently=False, html_message=content)

        return http_response(status=status.HTTP_201_CREATED, message=success_messages.EMAIL_SENT, data={
            "token": JWTUtil.encode({"email": email}, expiration_hours=24)
        })

    @action(methods=['get'], detail=False, url_path=r'verify-email/(?P<token>.*)', url_name='verify_email')
    def verify_email(self, request, *args, **kwargs):
        decoded_token = JWTUtil.decode(kwargs.get('token'))

        if decoded_token.get('from_email') is not True:
            raise drf_exceptions.PermissionDenied(error_messages.WRONG_TOKEN)

        serializer = UserSerializer(User.objects.save_email(**decoded_token))
        return http_response(status=status.HTTP_200_OK, message=success_messages.SUCCESS, data=serializer.data)

    @action(methods=['put'], detail=False, url_path='verify-phonenumber', url_name='verify_phonenumber')
    def verify_phonenumber(self, request):
        AuthUtil.is_auth(request)
        decoded_token = JWTUtil.decode(AuthUtil.get_token(request))

        user = User.objects.save_or_verify_phonenumber(email=decoded_token.get('email'), **request.data)
        if user.otp:
            send_sms(user.phonenumber, message=user.otp)

        serializer = UserSerializer(user)
        return http_response(status=status.HTTP_200_OK, message=success_messages.SUCCESS, data=serializer.data)

    @action(methods=['post'], detail=False, url_path='signup', url_name='signup')
    def create_user(self, request):
        serializer = UserSerializer(User.objects.create(**request.data))

        return http_response(status=status.HTTP_201_CREATED, data=serializer.data)

    @action(methods=['post'], detail=False, url_path='login', url_name='login')
    def login_user(self, request):
        user = User.objects.login(**request.data)
        if user.otp:
            content = loader.render_to_string('confirm_login.html', {'verification_code': user.otp})
            send_mail('Confirm login', '', settings.EMAIL_SENDER, [user.email], fail_silently=False, html_message=content)
            return http_response(status=status.HTTP_200_OK, message=success_messages.CONFIRM_LOGIN)
        serializer = UserSerializer(user)
        user_token = JWTUtil.encode({"email": user.email, "phonenumber": user.phonenumber}, expiration_hours=24)
        return http_response(status=status.HTTP_200_OK, data={
            "user": serializer.data,
            "token": user_token
        })
