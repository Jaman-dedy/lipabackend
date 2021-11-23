import urllib.parse
from rest_framework import exceptions as drf_exceptions
from rest_framework import viewsets, status
from rest_framework.decorators import action

from .models import User
from .serializers import BasicUserSerializer, UserSerializer
from bitlipa.utils.is_valid_uuid import is_valid_uuid
from bitlipa.utils.http_response import http_response
from bitlipa.resources import error_messages
from bitlipa.utils.auth_util import AuthUtil


class UserViewSet(viewsets.ViewSet):
    """
    API endpoint that allows users to be viewed/edited/deleted.
    """

    @action(methods=['put', 'get'], detail=False, url_path='*', url_name='list_update')
    def list_update(self, request):
        # list users
        if request.method == 'GET':
            AuthUtil.is_auth(request, is_admin=True)
            kwargs = {
                'page': request.GET.get('page'),
                'per_page': request.GET.get('per_page'),
                'first_name__iexact': request.GET.get('first_name'),
                'middle_name__iexact': request.GET.get('middle_name'),
                'last_name__iexact': request.GET.get('last_name'),
                'email__iexact': urllib.parse.unquote(request.GET.get('email')) if request.GET.get('email') else None,
                'phonenumber__iexact': urllib.parse.unquote(request.GET.get('phonenumber')) if request.GET.get('phonenumber') else None,
                'q': urllib.parse.unquote(request.GET.get('q')) if request.GET.get('q') else None
            }
            result = User.objects.list(user=request.user, **kwargs)
            serializer = UserSerializer(result.get('data'), many=True)
            return http_response(status=status.HTTP_200_OK, data=serializer.data, meta=result.get('meta'))

        # update user
        if request.method == 'PUT':
            AuthUtil.is_auth(request)
            user = User.objects.update(email=request.decoded_token.get('email'), **request.data)
            user_data = UserSerializer(user, context={'include_wallets': True}).data if user.id == request.user.id \
                else BasicUserSerializer(user, context={'include_wallets': True}).data
            return http_response(status=status.HTTP_200_OK, data=user_data)

    @action(methods=['get'], detail=False, url_path='admins', url_name='list_admin')
    def list_admins(self, request):
        AuthUtil.is_auth(request, is_admin=True)
        kwargs = {
            'page': request.GET.get('page'),
            'per_page': request.GET.get('per_page'),
            'first_name__iexact': request.GET.get('first_name'),
            'middle_name__iexact': request.GET.get('middle_name'),
            'last_name__iexact': request.GET.get('last_name'),
            'email__iexact': urllib.parse.unquote(request.GET.get('email')) if request.GET.get('email') else None,
            'phonenumber__iexact': urllib.parse.unquote(request.GET.get('phonenumber')) if request.GET.get('phonenumber') else None,
        }
        result = User.objects.list_admins(**kwargs)
        serializer = UserSerializer(result.get('data'), many=True)
        return http_response(status=status.HTTP_200_OK, data=serializer.data, meta=result.get('meta'))

    # get one user

    def retrieve(self, request, pk=None, **kwargs):
        AuthUtil.is_auth(request)
        user = None
        if pk == 'by_phonenumber' and request.GET.get('phonenumber'):
            user = User.objects.get(phonenumber__iexact=urllib.parse.unquote(request.GET.get('phonenumber')))

        if pk == 'by_email' and request.GET.get('email'):
            user = User.objects.get(email__iexact=urllib.parse.unquote(request.GET.get('email')))

        if pk == 'me':
            user = request.user

        if not user and is_valid_uuid(pk):
            user = User.objects.get(id=pk)

        if not user and not is_valid_uuid(pk):
            raise drf_exceptions.NotFound(error_messages.NOT_FOUND.format('user '))
        user_data = UserSerializer(user, context={'include_wallets': True}).data if user.id == request.user.id \
            else BasicUserSerializer(user, context={'include_wallets': True}).data
        return http_response(status=status.HTTP_200_OK, data=user_data)

    # update user
    def update(self, request, pk=None):
        AuthUtil.is_auth(request, is_admin=True)
        if pk and not is_valid_uuid(pk):
            raise drf_exceptions.NotFound(error_messages.NOT_FOUND.format('user '))

        user = User.objects.update(id=pk, **request.data)
        user_data = UserSerializer(user, context={'include_wallets': True}).data if user.id == request.user.id \
            else BasicUserSerializer(user, context={'include_wallets': True}).data
        return http_response(status=status.HTTP_200_OK, data=user_data)
