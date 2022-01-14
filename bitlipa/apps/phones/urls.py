from rest_framework import routers

from . import views


router = routers.DefaultRouter()

router.register(r'phones', views.PhoneViewSet, basename='phones')
urlpatterns = router.urls