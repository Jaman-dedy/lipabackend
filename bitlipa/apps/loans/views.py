from rest_framework import viewsets, status
from rest_framework.decorators import action
from django.db import transaction as db_transaction

from bitlipa.resources import error_messages
from bitlipa.utils.is_valid_uuid import is_valid_uuid
from bitlipa.utils.http_response import http_response
from bitlipa.utils.auth_util import AuthUtil
from .models import Loan
from .serializers import LoanSerializer


class LoanViewSet(viewsets.ViewSet):
    """
    API endpoint that allows loans to be viewed/edited/deleted.
    """
    @action(methods=['post', 'get'], detail=False, url_path='*', url_name='create_list_loans')
    def create_list_loans(self, request):
        # list loans
        if request.method == 'GET':
            return self.list_loans(request)

        # create loan
        if request.method == 'POST':
            return self.create_loan(request)

    @db_transaction.atomic
    def create_loan(self, request):
        AuthUtil.is_auth(request, is_admin=True)
        serializer = LoanSerializer(Loan.objects.create_loan(**request.data), many=True)
        return http_response(status=status.HTTP_201_CREATED, data=serializer.data)

    def list_loans(self, request):
        AuthUtil.is_auth(request, is_admin=True)
        kwargs = {
            'page': str(request.GET.get('page')),
            'per_page': str(request.GET.get('per_page')),
            'currency__iexact': request.GET.get('currency'),
        }
        result = Loan.objects.list(**kwargs)
        serializer = LoanSerializer(result.get('data'), many=True)
        return http_response(status=status.HTTP_200_OK, data=serializer.data, meta=result.get('meta'))

    # get one loan
    def retrieve(self, request, pk=None):
        AuthUtil.is_auth(request, is_admin=True)

        if pk and not is_valid_uuid(pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('loan '))

        loan = Loan.objects.get(id=pk)
        serializer = LoanSerializer(loan)
        return http_response(status=status.HTTP_200_OK, data=serializer.data)

    def update(self, request, pk=None):
        AuthUtil.is_auth(request, is_admin=True)

        if pk and not is_valid_uuid(pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('loan '))

        loan = Loan.objects.update(id=pk, **request.data)
        serializer = LoanSerializer(loan)

        return http_response(status=status.HTTP_200_OK, data=serializer.data)

    def delete(self, request, pk=None):
        AuthUtil.is_auth(request, is_admin=True)

        if pk and not is_valid_uuid(pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('loan '))

        loan = Loan.objects.remove(id=pk)
        serializer = LoanSerializer(loan)
        return http_response(status=status.HTTP_200_OK, data=serializer.data)
