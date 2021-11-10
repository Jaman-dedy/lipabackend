from rest_framework import routers

from . import views


router = routers.DefaultRouter()

router.register(r'enigma', views.EnigmaViewSet, basename='enigma')
urlpatterns = router.urls
