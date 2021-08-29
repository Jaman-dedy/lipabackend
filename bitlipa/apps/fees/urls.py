from rest_framework import routers

from . import views


router = routers.DefaultRouter()

router.register(r'fees', views.WalletViewSet, basename='fees')
urlpatterns = router.urls
