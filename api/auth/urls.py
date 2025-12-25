from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import TelegramTokenObtainPairView

urlpatterns = [
    path('telegram/token/', TelegramTokenObtainPairView.as_view(), name='token_telegram_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

