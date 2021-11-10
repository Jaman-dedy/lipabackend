from rest_framework import viewsets, status
from rest_framework.decorators import action


from bitlipa.utils.http_response import http_response
from .helpers import login as enigma_login


class EnigmaViewSet(viewsets.ViewSet):
    """
    API endpoint that allows enigma integration
    """
    @action(methods=['post'], detail=False, url_path='login', url_name='login')
    def login(self, request):
        response = enigma_login(**request.data)
        return http_response(status=status.HTTP_200_OK, data=response)
