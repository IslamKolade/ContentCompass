from django.urls import path
from .views import *
from rest_framework_simplejwt.views import (TokenRefreshView)


urlpatterns = [
    path('signup/', signup, name="signup"),
    path('login/', login, name="login"),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('refresh_access_token/', refresh_access_token, name='refresh_access_token'),
]
