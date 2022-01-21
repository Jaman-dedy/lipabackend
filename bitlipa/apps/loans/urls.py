from rest_framework import routers

from . import views


router = routers.DefaultRouter()

router.register(r'loans', views.LoanViewSet, basename='loans')
urlpatterns = router.urls
