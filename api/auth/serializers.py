from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser


class TelegramTokenObtainPairSerializer(serializers.Serializer):
    tg_token = serializers.CharField(required=True)

    def validate(self, attrs):
        tg_token = attrs.get("tg_token")
        user = CustomUser.objects.authenticate_by_tg_token(tg_token)
        if not user:
            raise AuthenticationFailed("Invalid Telegram token")

        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user_id": user.id,
            "tg_username": user.tg_username,
        }

