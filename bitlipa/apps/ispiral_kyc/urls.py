from rest_framework import routers

from . import views


router = routers.DefaultRouter()

router.register(r'ispiral', views.IspiralKycViewSet, basename='ispiral')
urlpatterns = router.urls
