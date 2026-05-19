from rest_framework.generics import ListAPIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from datetime import date, timedelta
from core.permissions import IsAdmin
from .models import ContactMessage, UserActivity
from .serializers import (
    GoogleAuthSerializer, UserSerializer, UserUpdateSerializer,
    SendEmailOTPSerializer, VerifyEmailOTPSerializer,
    ContactMessageSerializer, UserActivityResponseSerializer
)
from apps.accounts.guthub.serializers import GitHubAuthSerializer

User = get_user_model()  


def _jwt_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access":  str(refresh.access_token),
    }

@extend_schema(summary='Google Auth', tags=['Accounts'])
@method_decorator(csrf_exempt, name='dispatch')
class GoogleAuthView(GenericAPIView):
    permission_classes     = [AllowAny]
    authentication_classes = []
    serializer_class       = GoogleAuthSerializer

    @extend_schema(
        request=GoogleAuthSerializer,
        # security=[],
        responses={
            200: UserSerializer,
            201: UserSerializer,
            400: OpenApiResponse(description="Token yaroqsiz"),
        },
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user, created = serializer.get_or_create_user()

        return Response(
            {
                "user":    UserSerializer(user).data,
                "tokens":  _jwt_tokens(user),
                "created": created,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class MeView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class   = UserSerializer

    def get(self, request):
        return Response(self.get_serializer(request.user).data)

    def patch(self, request):
        serializer = UserUpdateSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data)

@extend_schema(summary='OTP yuborish', tags=['Accounts'])
class SendEmailOTPView(GenericAPIView):
    serializer_class = SendEmailOTPSerializer  # ✅ shu yoq qolgan edi

    def post(self, request):
        serializer = self.get_serializer(data=request.data)  # ✅ self.get_serializer

        if serializer.is_valid():
            return Response(
                {"message": "OTP emailga yuborildi"},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(summary='OTP tasdiqlash', tags=['Accounts'])
class VerifyEmailOTPView(GenericAPIView):
    serializer_class = VerifyEmailOTPSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            user, created = User.objects.get_or_create(email=email)

            if created or user.is_new_user:
                user.is_new_user = False
                user.save(update_fields=['is_new_user'])

            tokens = _jwt_tokens(user)

            return Response(
                {
                    "message": "OTP tasdiqlandi",
                    "email": user.email,
                    "full_name": user.get_full_name(),
                    "avatar_url": user.avatar_url.url if user.avatar_url else None,
                    "refresh": tokens['refresh'],
                    "access": tokens['access'],
                },
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@method_decorator(csrf_exempt, name='dispatch')
@extend_schema(summary='GitHub Auth', tags=['Accounts'])
class GitHubAuthView(GenericAPIView):
    permission_classes     = [AllowAny]
    authentication_classes = []
    serializer_class       = GitHubAuthSerializer

    @extend_schema(
        request=GitHubAuthSerializer,
        responses={
            200: UserSerializer,
            201: UserSerializer,
            400: OpenApiResponse(description="Token yaroqsiz"),
        },
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user, created = serializer.get_or_create_user()

        return Response(
            {
                "user":    UserSerializer(user).data,
                "tokens":  _jwt_tokens(user),
                "created": created,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
@extend_schema(summary='Contacts', tags=['Accounts'], request=ContactMessageSerializer)
class ContactMessageAPiView(APIView):
    def post(self, request):
        serializer = ContactMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Xabar yuborildi!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=400)

@extend_schema(summary='Contacts', tags=['Accounts'], request=ContactMessageSerializer)
class ContactMessageListView(ListAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [IsAdmin, IsAuthenticated]


class UserActivityView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: UserActivityResponseSerializer(many=True)},
        description="Foydalanuvchining oxirgi 1 yillik aktivligini qaytaradi."
    )
    def get(self, request):
        end_date = date.today()
        start_date = end_date.replace(year=end_date.year - 1)

        activities = UserActivity.objects.filter(
            user=request.user,
            date__range=(start_date, end_date)
        )
        activity_map = {a.date: a for a in activities}

        result = []
        current = start_date
        while current <= end_date:
            count = activity_map[current].count if current in activity_map else 0

            # Level mantiqi
            level = 0
            if count > 9: level = 4
            elif count > 6: level = 3
            elif count > 3: level = 2
            elif count > 0: level = 1

            result.append({
                "date": current.isoformat(),
                "count": count,
                "level": level
            })
            current += timedelta(days=1)

        return Response(result)