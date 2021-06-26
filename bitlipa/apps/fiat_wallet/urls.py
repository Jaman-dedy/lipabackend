from rest_framework import routers

from . import views


router = routers.DefaultRouter()

router.register(r'fiat-wallets', views.WalletViewSet, basename='fiat_wallet')
urlpatterns = router.urls
