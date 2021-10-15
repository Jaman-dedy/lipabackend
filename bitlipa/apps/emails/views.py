from rest_framework import viewsets, status
from rest_framework.decorators import action
from django.db import transaction as db_transaction

from bitlipa.resources import error_messages
from bitlipa.utils.is_valid_uuid import is_valid_uuid
from bitlipa.utils.http_response import http_response
from bitlipa.utils.auth_util import AuthUtil
from .models import Email
from .serializers import EmailSerializer


class WalletViewSet(viewsets.ViewSet):
    """
    API endpoint that allows emails to be created/viewed/deleted.
    """
    @action(methods=['post', 'get'], detail=False, url_path='*', url_name='create_list_emails')
    def create_list_emails(self, request):
        # list emails
        if request.method == 'GET':
            return self.list_emails(request)

        # create email
        if request.method == 'POST':
            return self.create_email(request)

    @db_transaction.atomic
    def create_email(self, request):
        AuthUtil.is_auth(request, is_admin=True)
        serializer = EmailSerializer(Email.objects.create_email(**request.data))
        return http_response(status=status.HTTP_201_CREATED, data=serializer.data)

    def list_emails(self, request):
        AuthUtil.is_auth(request, is_admin=True)
        kwargs = {
            'page': str(request.GET.get('page')),
            'per_page': str(request.GET.get('per_page')),
            'name__iexact': request.GET.get('name'),
            'type__iexact': request.GET.get('type'),
        }
        result = Email.objects.list(**kwargs)
        serializer = EmailSerializer(result.get('data'), many=True)
        return http_response(status=status.HTTP_200_OK, data=serializer.data, meta=result.get('meta'))

    # get one email
    def retrieve(self, request, pk=None):
        AuthUtil.is_auth(request, is_admin=True)

        if pk and not is_valid_uuid(pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('email '))

        email = Email.objects.get(id=pk)
        serializer = EmailSerializer(email)
        return http_response(status=status.HTTP_200_OK, data=serializer.data)

    def delete(self, request, pk=None):
        AuthUtil.is_auth(request, is_admin=True)

        if pk and not is_valid_uuid(pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('email '))

        email = Email.objects.remove(id=pk)
        serializer = EmailSerializer(email)
        return http_response(status=status.HTTP_200_OK, data=serializer.data)
