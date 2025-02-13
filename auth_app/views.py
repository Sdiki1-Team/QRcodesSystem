from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth import authenticate
from rest_framework import serializers

from .serializers import RegisterSerializer, LoginSerializer, PingSerializer, RefreshTokenSerializer



class RegisterView(APIView):
    @swagger_auto_schema(
        operation_description="Регистрация новогопользователя",
        request_body=RegisterSerializer,
        responses={
            201: "Пользователь успешно зарегистрирован",
            400: "Неверные данные"
        }
    )

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User registred successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    @swagger_auto_schema(
        operation_description="Аворизация пользователя",
        request_body=LoginSerializer,
        responses={
            200: "Успешный вход",
            400: "Неверный логин или пароль"
        }
    )

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(username=serializer.validated_data['username'], password=serializer.validated_data['password'])
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'access_token': str(refresh.access_token),
                    'refresh_token': str(refresh),
                })
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RefreshTokenView(APIView):
    @swagger_auto_schema(
        operation_description="Обновление access token с использоаанием refresh token",
        request_body=RefreshTokenSerializer,
        responses={
            200: "Успешное обновление токенов",
            490: "Ошибка обновления токенов",
        }
    )

    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response({"error": "refresh_token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            return Response({"access_token": access_token}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST)
        

class PingView(APIView):
    @swagger_auto_schema(
        operation_description="Проверка состояния сервера",
        responses={
            200: "Сервер работает",
            401: "Неавторизован",
        }
    )

    def get(self, request):
        return Response({"status": "auth"}, status=status.HTTP_200_OK)
