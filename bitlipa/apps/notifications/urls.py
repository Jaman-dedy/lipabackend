from rest_framework import routers

from . import views


router = routers.DefaultRouter()

router.register(r'notifications', views.NotificationViewSet, basename='notifications')
urlpatterns = router.urls
