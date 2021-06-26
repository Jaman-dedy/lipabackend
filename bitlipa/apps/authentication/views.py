from rest_framework import viewsets, status
from rest_framework.decorators import action
from django.core.mail import send_mail
from django.template import loader

from bitlipa import settings
from bitlipa.resources import success_messages
from bitlipa.utils.jwt_util import JWTUtil
from bitlipa.utils.http_response import http_response
from bitlipa.apps.users.models import User
from bitlipa.apps.users.serializers import UserSerializer


class AuthViewSet(viewsets.ViewSet):
    """
    API endpoint that allows users to be registered/login.
    """

    @action(methods=['post'], detail=False, url_path='send-email-verification-link', url_name='send_email_verification_link')
    def send_email_verification_link(self, request):
        token = JWTUtil.encode({"email": request.data.get('email')}, expiration_hours=24)
        content = loader.render_to_string('verify_email.html', {'verification_link': f'{settings.API_URL}/auth/verify-email/{token}/'})
        send_mail('Verify account', '', settings.EMAIL_SENDER, [request.data.get('email')], fail_silently=False, html_message=content)
        return http_response(status=status.HTTP_201_CREATED, message=success_messages.EMAIL_SENT)

    @action(methods=['get'], detail=False, url_path=r'verify-email/(?P<token>.*)', url_name='verify-email')
    def verify_email(self, request, *args, **kwargs):
        decoded_token = JWTUtil.decode(kwargs.get('token'))

        serializer = UserSerializer(User.objects.save_email(**decoded_token))

        return http_response(status=status.HTTP_200_OK, message=success_messages.SUCCESS, data=serializer.data)

    # TODO: Implement send SMS
    @action(methods=['get'], detail=False, url_path='verify-phonenumber', url_name='verify-phonenumber')
    def verify_phonenumber(self, request):
        return http_response(status=status.HTTP_201_CREATED, message='sent')

    @action(methods=['post'], detail=False, url_path='signup', url_name='signup')
    def create_user(self, request):
        serializer = UserSerializer(User.objects.create(**request.data))

        return http_response(status=status.HTTP_201_CREATED, data=serializer.data)

    @action(methods=['post'], detail=False, url_path='login', url_name='login')
    def login_user(self, request):
        serializer = UserSerializer(User.objects.login(**request.data))
        user_token = JWTUtil.encode({"email": request.data.get('email')}, expiration_hours=24)
        return http_response(status=status.HTTP_200_OK, data={
            "user": serializer.data,
            "token": user_token
        })
