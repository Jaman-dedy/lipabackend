from rest_framework import viewsets, status
from rest_framework.decorators import action

from .models import Phone
from .serializers import PhoneSerializer
from bitlipa.utils.is_valid_uuid import is_valid_uuid
from bitlipa.utils.http_response import http_response
from bitlipa.resources import error_messages
from bitlipa.utils.auth_util import AuthUtil


class PhoneViewSet(viewsets.ViewSet):
    """
    API endpoint that allows phone to be viewed/edited/deleted.
    """
    @action(methods=['post', 'get'], detail=False, url_path='*', url_name='create_list_update_phones')
    def create_list_phone(self, request):
        # list phones
        if request.method == 'GET':
            return self.list_phones(request)

        # create phone
        if request.method == 'POST':
            return self.create_phone(request)

    def create_phone(self, request):
        AuthUtil.is_auth(request)

        serializer = PhoneSerializer(Phone.objects.create_phone(user=request.user, **request.data))

        return http_response(status=status.HTTP_201_CREATED, data=serializer.data)

    def list_phones(self, request):
        AuthUtil.is_auth(request)

        phone = Phone.objects.filter(email=request.decoded_token.get('email'))
        serializer = PhoneSerializer(phone, many=True)

        return http_response(status=status.HTTP_200_OK, data=serializer.data)

    # get one phone
    def retrieve(self, request, pk=None):
        if pk and not is_valid_uuid(pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('phone '))

        AuthUtil.is_auth(request)

        if request.decoded_token is None:
            return http_response(status=status.HTTP_400_BAD_REQUEST, message=error_messages.WRONG_TOKEN)

        phone = Phone.objects.get(id=pk)
        serializer = PhoneSerializer(phone)

        return http_response(status=status.HTTP_200_OK, data=serializer.data)

    def update(self, request, pk=None):
        if pk and not is_valid_uuid(pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('phone '))

        AuthUtil.is_auth(request)

        if request.decoded_token is None:
            return http_response(status=status.HTTP_400_BAD_REQUEST, message=error_messages.WRONG_TOKEN)

        phone = Phone.objects.update(id=pk, **request.data)
        serializer = PhoneSerializer(phone)

        return http_response(status=status.HTTP_200_OK, data=serializer.data)

    def delete(self, request, pk=None):
        if pk and not is_valid_uuid(pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('user '))
        AuthUtil.is_auth(request)

        phone = Phone.objects.delete(id=pk)
        serializer = PhoneSerializer(phone)

        return http_response(status=status.HTTP_200_OK, data=serializer.data)
