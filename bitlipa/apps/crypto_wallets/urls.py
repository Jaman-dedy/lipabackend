from rest_framework import routers

from . import views


router = routers.DefaultRouter()

router.register(r'crypto-wallets', views.WalletViewSet, basename='crypto_wallets')
urlpatterns = router.urls
