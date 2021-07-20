from django.urls import include, path
from rest_framework import routers


router = routers.DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('', include('bitlipa.apps.authentication.urls')),
    path('', include('bitlipa.apps.users.urls')),
    path('', include('bitlipa.apps.fiat_wallet.urls')),
    path('', include('bitlipa.apps.crypto_wallets.urls')),
    path('', include('bitlipa.apps.transactions.urls')),
]
