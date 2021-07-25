from rest_framework import routers

from . import views


router = routers.DefaultRouter()

router.register(r'transactions', views.TransactionViewSet, basename='transactions')
urlpatterns = router.urls
