from rest_framework import routers

from . import views


router = routers.DefaultRouter()

router.register(r'transaction-limits', views.WalletViewSet, basename='transaction_limits')
urlpatterns = router.urls
