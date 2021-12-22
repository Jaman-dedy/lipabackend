from django.urls import include, path
from rest_framework import routers


router = routers.DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('', include('bitlipa.apps.authentication.urls')),
    path('', include('bitlipa.apps.users.urls')),
    path('', include('bitlipa.apps.global_configs.urls')),
    path('', include('bitlipa.apps.fiat_wallets.urls')),
    path('', include('bitlipa.apps.crypto_wallets.urls')),
    path('', include('bitlipa.apps.transactions.urls')),
    path('', include('bitlipa.apps.currency_exchange.urls')),
    path('', include('bitlipa.apps.fees.urls')),
    path('', include('bitlipa.apps.ispiral_kyc.urls')),
    path('', include('bitlipa.apps.roles.urls')),
    path('', include('bitlipa.apps.user_role.urls')),
    path('', include('bitlipa.apps.notifications.urls')),
    path('', include('bitlipa.apps.emails.urls')),
    path('', include('bitlipa.apps.transaction_limits.urls')),
    path('', include('bitlipa.apps.user_activity.urls')),
    path('', include('bitlipa.apps.enigma.urls')),
]
