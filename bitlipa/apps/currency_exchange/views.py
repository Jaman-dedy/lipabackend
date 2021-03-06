from rest_framework import viewsets, status
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from rest_framework.decorators import action

from .models import CurrencyExchange
from .serializers import CurrencyExchangeSerializer
from bitlipa.utils.is_valid_uuid import is_valid_uuid
from bitlipa.utils.http_response import http_response
from bitlipa.resources import error_messages
from bitlipa.utils.auth_util import AuthUtil
from .tasks import update_exchange_rates

# api_key='d2cXIfAXzL7oMWf6W1hOeHeOW5YBQ64zV3ZVxdg5t2ELs3dlVr2FgIZDINMKWmX9'
# api_secret='RCPq5jvJ5gRkdbcKmpHXqoQ4ajrAIEiP1KrUwPNz728FWR0knpYMforhB9QhBj4E'
api_key='dddd'
api_secret='ddd'


class CurrencyExchangeViewSet(viewsets.ViewSet):
    """
    API endpoint that allows currency exchange to be viewed/edited/deleted.
    """
    @action(methods=['post', 'get', 'put'], detail=False, url_path='*', url_name='create_list_exchange_rates')
    def create_list_exchange_rates(self, request):
        # list exchange rates
        if request.method == 'GET':
            return self.list_exchange_rates(request)

        # create exchange rate
        if request.method == 'POST':
            return self.create_exchange_rate(request)

    def create_exchange_rate(self, request):
        AuthUtil.is_auth(request, True)

        serializer = CurrencyExchangeSerializer(CurrencyExchange.objects.create_exchange_rate(**request.data))

        return http_response(status=status.HTTP_201_CREATED, data=serializer.data)

    def list_exchange_rates(self, request):
        AuthUtil.is_auth(request)
        table_fields = {}
        if request.GET.get('currency'):
            table_fields['base_currency__iexact'] = request.GET.get('currency')
        currency_exchange = CurrencyExchange.objects.filter(**table_fields).order_by('-created_at')
        serializer = CurrencyExchangeSerializer(currency_exchange, many=True)

        return http_response(status=status.HTTP_200_OK, data=serializer.data)

    # get one exchange rate
    def retrieve(self, request, pk=None):
        if pk and not is_valid_uuid(pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('exchange rate '))

        AuthUtil.is_auth(request)

        if request.decoded_token is None:
            return http_response(status=status.HTTP_400_BAD_REQUEST, message=error_messages.WRONG_TOKEN)

        currency_exchange = CurrencyExchange.objects.get(id=pk)
        serializer = CurrencyExchangeSerializer(currency_exchange)

        return http_response(status=status.HTTP_200_OK, data=serializer.data)

    def update(self, request, pk=None):
        AuthUtil.is_auth(request, True)

        if pk and not is_valid_uuid(pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('exchange rate '))

        if request.decoded_token is None:
            return http_response(status=status.HTTP_400_BAD_REQUEST, message=error_messages.WRONG_TOKEN)

        currency_exchange = CurrencyExchange.objects.update(id=pk, **request.data)
        serializer = CurrencyExchangeSerializer(currency_exchange)

        return http_response(status=status.HTTP_200_OK, data=serializer.data)

    def delete(self, request, pk=None):
        AuthUtil.is_auth(request, True)

        if pk and not is_valid_uuid(pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('user '))

        currency_exchange = CurrencyExchange.objects.delete(id=pk)
        serializer = CurrencyExchangeSerializer(currency_exchange)

        return http_response(status=status.HTTP_200_OK, data=serializer.data)

    @action(methods=['post'], detail=False, url_path='convert', url_name='convert')
    def convert(self, request):
        AuthUtil.is_auth(request)
        currency_exchange = CurrencyExchange.objects.convert(**request.data)

        return http_response(status=status.HTTP_200_OK, data=currency_exchange)

    @action(methods=['post'], detail=False, url_path='exchange', url_name='exchange')
    def exchange(self, request):
        AuthUtil.is_auth(request)
        client = Client(api_key, api_secret)
        currency_exchange = CurrencyExchange.objects.convert(**request.data)
        
        order = client.create_order(
            symbol='BTCUSDT',
            side=Client.SIDE_SELL,
            type=Client.ORDER_TYPE_MARKET,
            quantity=0.00024,
        )

        return http_response(status=status.HTTP_200_OK, data=order)

    @action(methods=['put'], detail=False, url_path='update-rates', url_name='update_rates')
    def update_rates(self, request):
        AuthUtil.is_auth(request, True)
        return http_response(status=status.HTTP_200_OK, data=update_exchange_rates(True))
