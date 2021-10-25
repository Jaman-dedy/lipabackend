from django.urls import include, path
from rest_framework import routers

from bitlipa.apps import notifications


router = routers.DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('', include('bitlipa.apps.authentication.urls')),
    path('', include('bitlipa.apps.users.urls')),
    path('', include('bitlipa.apps.fiat_wallet.urls')),
    path('', include('bitlipa.apps.crypto_wallets.urls')),
    path('', include('bitlipa.apps.transactions.urls')),
    path('', include('bitlipa.apps.currency_exchange.urls')),
    path('', include('bitlipa.apps.fees.urls')),
    path('', include('bitlipa.apps.ispiral_kyc.urls')),
    path('', include('bitlipa.apps.roles.urls')),
    path('', include('bitlipa.apps.user_role.urls')),
    path('', include('bitlipa.apps.notifications.urls'))
]
