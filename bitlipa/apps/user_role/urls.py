from rest_framework import routers

from . import views


router = routers.DefaultRouter()

router.register(r'user-roles', views.UserRoleViewSet, basename='user-roles')
urlpatterns = router.urls
