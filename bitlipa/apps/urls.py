from django.urls import include, path
from rest_framework import routers


router = routers.DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('', include('bitlipa.apps.authentication.urls')),
    path('', include('bitlipa.apps.users.urls')),
]
