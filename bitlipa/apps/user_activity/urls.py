from rest_framework import routers

from . import views


router = routers.DefaultRouter()

router.register(r'user-activity', views.UserActivityViewSet, basename='user-activity')
urlpatterns = router.urls
