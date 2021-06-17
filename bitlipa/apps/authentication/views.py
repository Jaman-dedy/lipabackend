from rest_framework import viewsets, status
from rest_framework.decorators import action

from bitlipa.resources import error_messages, success_messages
from bitlipa.utils.get_object_attr import get_object_attr
from bitlipa.utils.jwt import encode as jwt_encode, decode as jwt_decode
from bitlipa.utils.http_response import http_response
from bitlipa.apps.users.models import User
from bitlipa.apps.users.serializers import UserSerializer


class AuthViewSet(viewsets.ViewSet):
    """
    API endpoint that allows users to be registered/login.
    """

    # TODO: Implement send email
    @action(methods=['post'], detail=False, url_path='send-email-verification-link', url_name='send_email_verification_link')
    def send_email_verification_link(self, request):
        try:
            return http_response(status=status.HTTP_201_CREATED, message=success_messages.EMAIL_SENT, data={
                "token": jwt_encode({"email": request.data.get('email')}, expiration_hours=24),
                "expires_in": "24 hours"
            })
        except Exception as e:
            return http_response(status=status.HTTP_400_BAD_REQUEST, message=str(get_object_attr(e, 'message', e)))

    @action(methods=['get'], detail=False, url_path=r'verify-email/(?P<token>.*)', url_name='verify-email')
    def verify_email(self, request, *args, **kwargs):
        try:
            decoded_token = jwt_decode(kwargs.get('token'))

            if decoded_token is None:
                return http_response(status=status.HTTP_400_BAD_REQUEST, message=error_messages.WRONG_TOKEN)
            serializer = UserSerializer(User.objects.save_email(**decoded_token))

            return http_response(status=status.HTTP_200_OK, message=success_messages.SUCCESS, data=serializer.data)
        except Exception as e:
            return http_response(status=status.HTTP_400_BAD_REQUEST, message=str(get_object_attr(e, 'message', e)))

    # TODO: Implement send SMS
    @action(methods=['get'], detail=False, url_path='verify-phonenumber', url_name='verify-phonenumber')
    def verify_phonenumber(self, request):
        try:
            return http_response(status=status.HTTP_201_CREATED, message='sent')
        except Exception as e:
            return http_response(status=status.HTTP_400_BAD_REQUEST, message=str(get_object_attr(e, 'message', e)))

    @action(methods=['post'], detail=False, url_path='signup', url_name='signup')
    def create_user(self, request):
        try:
            serializer = UserSerializer(User.objects.create(**request.data))

            return http_response(status=status.HTTP_201_CREATED, data=serializer.data)
        except Exception as e:
            return http_response(status=status.HTTP_400_BAD_REQUEST, message=str(get_object_attr(e, 'message', e)))
    
    @action(methods=['post'], detail=False, url_path='login', url_name='login')
    def login_user(self, request):
        try:
            serializer = UserSerializer(User.objects.login(**request.data))
            userToken = jwt_encode({"email": request.data.get('email')}, expiration_hours=24)
            return http_response(status=status.HTTP_200_OK, data={
                "user": serializer.data,
                "token": userToken
            })
        except User.DoesNotExist:
            return http_response(status=status.HTTP_400_BAD_REQUEST, message=error_messages.WRONG_CREDENTAILS)
        except Exception as e:
            return http_response(status=status.HTTP_400_BAD_REQUEST, message=str(get_object_attr(e, 'message', e)))
