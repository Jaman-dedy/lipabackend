from rest_framework import routers

from . import views


router = routers.DefaultRouter()

router.register(r'auth', views.AuthViewSet, basename='auth')
urlpatterns = router.urls
