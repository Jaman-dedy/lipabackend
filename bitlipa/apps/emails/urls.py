from rest_framework import routers

from . import views


router = routers.DefaultRouter()

router.register(r'emails', views.WalletViewSet, basename='emails')
urlpatterns = router.urls
