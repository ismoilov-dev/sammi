from rest_framework import serializers
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.conf import settings
from .models import User, ContactMessage, UserActivity
from .utils import send_otp_email, verify_otp


class GoogleAuthSerializer(serializers.Serializer):
    token         = serializers.CharField(required=True)


    def validate_token(self, token):
        client_id = settings.SOCIALACCOUNT_PROVIDERS["google"]["APP"]["client_id"]

        try:
            idinfo = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                client_id,
                clock_skew_in_seconds=10,
            )
        except ValueError as e:
            raise serializers.ValidationError(f"Token yaroqsiz: {e}")

        if idinfo.get("aud") != client_id:
            raise serializers.ValidationError("Token boshqa ilovaga tegishli.")

        return idinfo

    def get_or_create_user(self):
        idinfo        = self.validated_data["token"]
        language_code = self.validated_data.get("language_code", "en")

        email      = idinfo.get("email", "")
        full_name  = idinfo.get("name", "")
        avatar_url = idinfo.get("picture", "")

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "full_name":     full_name,
                "avatar_url":    avatar_url,
                "language_code": language_code,
                "is_active":     True,
                "is_new_user":   True,
            },
        )

        if not created:
            update_fields = []

            if avatar_url and user.avatar_url != avatar_url:
                user.avatar_url = avatar_url
                update_fields.append("avatar_url")

            if user.is_new_user:
                user.is_new_user = False
                update_fields.append("is_new_user")

            if update_fields:
                user.save(update_fields=update_fields)

        return user, created


class UserSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    def get_avatar_url(self, obj):
        if obj.avatar_url:
            try:
                return obj.avatar_url.url
            except Exception:
                return None
        return None

    class Meta:
        model        = User
        fields       = ["id", "email", "full_name", "avatar_url", "country", "language_code", "created_at", "is_new_user"]
        read_only_fields = ["id", "email", "created_at", "is_new_user"]

class UserUpdateSerializer(serializers.ModelSerializer):
    """PATCH /auth/me/ uchun"""
    class Meta:
        model  = User
        fields = ["full_name", "avatar_url", "country", "language_code"]


class SendEmailOTPSerializer(serializers.Serializer):  # ✅ 's' olib tashlandi
    email = serializers.EmailField()

    def validate(self, attrs):  # ✅ attrs ishlatildi
        email = attrs.get('email')
        send_otp_email(email)
        return attrs


class VerifyEmailOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()

    def validate(self, data):
        email = data.get("email")
        otp = data.get("otp")

        if not verify_otp(email, otp):
            raise serializers.ValidationError("OTP noto'g'ri yoki eskirgan")

        return data
    
# Contact Us Message

class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ['id', 'name', 'email', 'message', 'created_at']
        read_only_fields = ['created_at']

class UserActivityResponseSerializer(serializers.ModelSerializer):
    level = serializers.SerializerMethodField()

    class Meta:
        model = UserActivity
        fields = ['date', 'count', 'level']

    def get_level(self, obj):
        if obj.count == 0:
            return 0
        if obj.count <= 3:
            return 1
        if obj.count <= 6:
            return 2
        if obj.count <= 9:
            return 3
        return 4