from django.urls import path
from django.views.generic.base import TemplateView
from .views import *


urlpatterns = [
    path('user_data/', user_data, name='user_data'),
    path('wallet/fund/', fund_wallet, name='fund_wallet'),
    path('subscriptions/', subscriptions, name='subscriptions'),
    path('subscriptions/<int:id>/', subscription, name='subscription'),
    path('admin-interface/logo/logo.svg', redirect_logo, name="redirect_logo"),
    path('admin-interface/favicon/logo.svg', redirect_favicon, name="redirect_favicon"),
]