from rest_framework import routers

from . import views


router = routers.DefaultRouter()

router.register(r'roles', views.RoleViewSet, basename='roles')
urlpatterns = router.urls
