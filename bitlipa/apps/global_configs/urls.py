from rest_framework import routers

from . import views


router = routers.DefaultRouter()

router.register(r'global-configs', views.GlobalConfigSet, basename='global_configs')
urlpatterns = router.urls
