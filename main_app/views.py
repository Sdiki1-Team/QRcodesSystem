from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import ObjectSerializer, WorkSerializer, ReviewSerializer
from .models import CustomUser, Object, Work, Review
# Create your views here.






class GetStatusWork(APIView):
    @swagger_auto_schema(
        tags=['work'],
        operation_description="Получить статус объекта",
        request_body=WorkSerializer,
        responses={200: "Работа завершена", 400: "Ошибка завершения работы"}
    )

    def get(self, request, work_id):
        ...

class StartWorkView(APIView):
    @swagger_auto_schema(
        tags=['work'],
        operation_description="Начало работы на объекте",
        request_body=WorkSerializer,
        responses={200: "Работа началась", 400: "Ошибка начала работы"}
    )

    def post(self, request):
        object_id = request.data.get('object')
        user_id = request.user.id

        # Проверка, не работает ли уже пользователь на другом объекте
        if Work.objects.filter(user_id=user_id, end_time__isnull=True).exists():
            return Response({'error': 'Пользователь уже работает на другом объекте.'}, status=status.HTTP_400_BAD_REQUEST)

        work = Work.objects.create(object_id=object_id, user_id=user_id)
        work.start_work()
        return Response({"detail": "Работа началась"}, status=status.HTTP_200_OK)

# Завершение работы
class EndWorkView(APIView):
    @swagger_auto_schema(
        tags=['work'],
        operation_description="Завершение работы на объекте",
        request_body=WorkSerializer,
        responses={200: "Работа завершена", 400: "Ошибка завершения работы"}
    )
    def post(self, request):
        object_id = request.data.get('object')
        user_id = request.user.id

        work = Work.objects.filter(object_id=object_id, user_id=user_id, end_time__isnull=True).first()
        if work:
            work.end_work()
            return Response({"detail": "Работа завершена"}, status=status.HTTP_200_OK)
        return Response({'error': 'Работа не найдена или уже завершена'}, status=status.HTTP_400_BAD_REQUEST)

# Оценка работы
class ReviewView(APIView):
    @swagger_auto_schema(
        tags=['review'],
        operation_description="Оценка работы",
        request_body=ReviewSerializer,
        responses={200: "Оценка успешно оставлена", 400: "Ошибка оценки"}
    )
    def post(self, request, work_id):
        review_data = request.data
        review_data['work'] = work_id
        serializer = ReviewSerializer(data=review_data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Оценка успешно оставлена"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

