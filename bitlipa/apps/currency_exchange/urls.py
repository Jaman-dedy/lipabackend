from rest_framework import routers

from . import views


router = routers.DefaultRouter()

router.register(r'currency-exchange', views.CurrencyExchangeViewSet, basename='currency_exchange')
urlpatterns = router.urls
