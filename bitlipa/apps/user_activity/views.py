from rest_framework import viewsets, status
from rest_framework.decorators import action

from .models import UserActivity
from .serializers import UserActivitySerializer
from bitlipa.utils.is_valid_uuid import is_valid_uuid
from bitlipa.utils.http_response import http_response
from bitlipa.resources import error_messages
from bitlipa.utils.auth_util import AuthUtil


class UserActivityViewSet(viewsets.ViewSet):
    """
    API endpoint that allows user activity to be viewed/deleted.
    """
    @action(methods=['get'], detail=False, url_path='*', url_name='list_user_activity')
    def list_user_activity(self, request):
        AuthUtil.is_auth(request, is_admin=True)

        user_activity = UserActivity.objects.all().order_by('-created_at')
        serializer = UserActivitySerializer(user_activity, many=True)

        return http_response(status=status.HTTP_200_OK, data=serializer.data)

    def delete(self, request, pk=None):
        if pk and not is_valid_uuid(pk):
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('user '))
        AuthUtil.is_auth(request, is_admin=True)

        user_activity = UserActivity.objects.delete(id=pk)
        serializer = UserActivitySerializer(user_activity)

        return http_response(status=status.HTTP_200_OK, data=serializer.data)
