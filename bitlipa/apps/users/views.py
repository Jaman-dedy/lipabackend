from rest_framework import viewsets, status
from rest_framework.decorators import action

from .models import User
from .serializers import UserSerializer
from bitlipa.utils.is_valid_uuid import is_valid_uuid
from bitlipa.utils.get_object_attr import get_object_attr
from bitlipa.utils.http_response import http_response
from bitlipa.utils.jwt import decode as jwt_decode
from bitlipa.resources import error_messages


class UserViewSet(viewsets.ViewSet):
    """
    API endpoint that allows users to be viewed/edited/deleted.
    """

    @action(methods=['put', 'get'], detail=False, url_path='*', url_name='list_update')
    def list_update(self, request):
        serializer = UserSerializer()
        try:
            # list users
            if request.method == 'GET':
                queryset = User.objects.all().order_by('-created_at')
                serializer = UserSerializer(queryset, many=True)

            # update user
            if request.method == 'PUT':
                token = request.headers.get("Authorization", default="").replace('Bearer', '').strip()
                if not token:
                    return http_response(status=status.HTTP_401_UNAUTHORIZED, message=error_messages.AUTHENTICATION_REQUIRED)

                decoded_token = jwt_decode(token)

                if decoded_token is None:
                    return http_response(status=status.HTTP_400_BAD_REQUEST, message=error_messages.WRONG_TOKEN)

                user = User.objects.update(email=decoded_token.get('email'), **request.data)
                if user is None:
                    return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('user '))
                serializer = UserSerializer(user)

            return http_response(status=status.HTTP_200_OK, data=serializer.data)

        except User.DoesNotExist:
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('user '))
        except Exception as e:
            return http_response(status=status.HTTP_400_BAD_REQUEST, message=str(get_object_attr(e, 'message', e)))

    # get one user
    def retrieve(self, request, pk=None):
        try:

            if not is_valid_uuid(pk):
                return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('user '))

            user = User.objects.get(id=pk)

            serializer = UserSerializer(user)

            return http_response(status=status.HTTP_200_OK, data=serializer.data)
        except User.DoesNotExist:
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('user '))
        except Exception as e:
            return http_response(status=status.HTTP_400_BAD_REQUEST, message=str(get_object_attr(e, 'message', e)))

    # update user
    def update(self, request, pk=None):
        try:
            if pk and not is_valid_uuid(pk):
                return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('user '))

            user = User.objects.update(id=pk, **request.data)
            serializer = UserSerializer(user)

            return http_response(status=status.HTTP_200_OK, data=serializer.data)
        except User.DoesNotExist:
            return http_response(status=status.HTTP_404_NOT_FOUND, message=error_messages.NOT_FOUND.format('user '))
        except Exception as e:
            return http_response(status=status.HTTP_400_BAD_REQUEST, message=str(get_object_attr(e, 'message', e)))
