from rest_framework import viewsets, status
from rest_framework.decorators import action

from .models import Notification
from .serializers import NotificationSerializer
from bitlipa.utils.is_valid_uuid import is_valid_uuid
from bitlipa.utils.http_response import http_response
from bitlipa.resources import error_messages
from bitlipa.utils.auth_util import AuthUtil


class NotificationViewSet(viewsets.ViewSet):
    """
    API endpoint that allows notifications to be viewed/edited/deleted.
    """
    @action(methods=['post', 'get'], detail=False, url_path='*', url_name='create_list_update_notifications')
    def create_list_notifications(self, request):
        # list notifications
        if request.method == 'GET':
            return self.list_notifications(request)

        # create wallet
        if request.method == 'POST':
            return self.create_notification(request)

    def create_notification(self, request):
        AuthUtil.is_auth(request)

        serializer = NotificationSerializer(Notification.objects.create_notification(user=request.user, **request.data))

        return http_response(status=status.HTTP_201_CREATED, data=serializer.data)

    def list_notifications(self, request):
        AuthUtil.is_auth(request)

        notification = Notification.objects.all().order_by('-created_at')
        serializer = NotificationSerializer(notification, many=True)

        return http_response(status=status.HTTP_200_OK, data=serializer.data)

    # get one wallet
    def retrieve(self, request, pk=None):
        if pk and not is_valid_uuid(pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('notification '))

        AuthUtil.is_auth(request)

        if request.decoded_token is None:
            return http_response(status=status.HTTP_400_BAD_REQUEST, message=error_messages.WRONG_TOKEN)

        notification = Notification.objects.get(id=pk)
        serializer = NotificationSerializer(notification)

        return http_response(status=status.HTTP_200_OK, data=serializer.data)

    def update(self, request, pk=None):
        if pk and not is_valid_uuid(pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('notifiction '))

        AuthUtil.is_auth(request)

        if request.decoded_token is None:
            return http_response(status=status.HTTP_400_BAD_REQUEST, message=error_messages.WRONG_TOKEN)

        notification = Notification.objects.update(id=pk, **request.data)
        serializer = NotificationSerializer(notification)

        return http_response(status=status.HTTP_200_OK, data=serializer.data)

    def delete(self, request, pk=None):
        if pk and not is_valid_uuid(pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('user '))
        AuthUtil.is_auth(request)

        notification = Notification.objects.delete(id=pk)
        serializer = NotificationSerializer(notification)

        return http_response(status=status.HTTP_200_OK, data=serializer.data)
