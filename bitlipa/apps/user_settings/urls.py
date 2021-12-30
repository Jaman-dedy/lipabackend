from rest_framework import routers

from . import views


router = routers.DefaultRouter()

router.register(r'user-settings', views.UserSettingViewSet, basename='user_settings')
urlpatterns = router.urls
