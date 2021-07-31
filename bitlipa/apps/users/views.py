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
        AuthUtil.is_auth(request)

        # list users
        if request.method == 'GET':
            kwargs = {
                'page': request.GET.get('page'),
                'per_page': request.GET.get('per_page'),
                'first_name__iexact': request.GET.get('first_name'),
                'middle_name__iexact': request.GET.get('middle_name'),
                'last_name__iexact': request.GET.get('last_name'),
                'email__iexact': request.GET.get('email'),
                'phonenumber__iexact': request.GET.get('phonenumber'),
            }
            result = User.objects.list(user=request.user, **kwargs)
            serializer = UserSerializer(result.get('data'), many=True)
            return http_response(status=status.HTTP_200_OK, data=serializer.data, meta=result.get('meta'))

        # update user
        if request.method == 'PUT':
            user = User.objects.update(email=request.decoded_token.get('email'), **request.data)
            return http_response(status=status.HTTP_200_OK, data=UserSerializer(user).data)

    # get one user
    def retrieve(self, request, pk=None):
        AuthUtil.is_auth(request)
        user = None
        if pk == 'by_phonenumber' and request.GET.get('phonenumber'):
            user = User.objects.get(phonenumber__iexact=request.GET.get('phonenumber'))

        if pk == 'by_email' and request.GET.get('email'):
            user = User.objects.get(email__iexact=request.GET.get('email'))

        if pk == 'me':
            user = request.user

        if not user and is_valid_uuid(pk):
            user = User.objects.get(id=pk)

        if not user and not is_valid_uuid(pk):
            raise drf_exceptions.NotFound(error_messages.NOT_FOUND.format('user '))
        user_data = UserSerializer(user).data if user.id == request.user.id else BasicUserSerializer(user).data
        return http_response(status=status.HTTP_200_OK, data=user_data)

    # update user
    def update(self, request, pk=None):
        AuthUtil.is_auth(request)
        if pk and not is_valid_uuid(pk):
            raise drf_exceptions.NotFound(error_messages.NOT_FOUND.format('user '))

        user = User.objects.update(id=pk, **request.data)

        return http_response(status=status.HTTP_200_OK, data=UserSerializer(user).data)
