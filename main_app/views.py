import stat
from urllib import response
from xml.dom import NotFoundErr
from rest_framework import status, generics, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import PermissionDenied, NotFound

from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from .serializers import (
    WorkSerializer,
    ReviewSerializer,
    WorkImageSerializer,
    WorkImageListSerializer,
    StartWorkSerializer,
    EndWorkSerializer,
    ObjectSerializer,
    StatusResponseSerializer,
    WorkHistorySerializer,
    WorkWithReviewAndImagesSerializer
)
from .models import Work, WorkImage, Object
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class StartWorkView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        security=[{"Bearer": []}],
        tags=["Work"],
        operation_description="Начало работы на объекте",
        request_body=StartWorkSerializer,
        responses={
            200: "Работа началась",
            400: "Ошибка валидации",
            403: "Доступ запрещен",
        },
    )
    def post(self, request):
        serializer = StartWorkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        object_id = serializer.validated_data["object"]
        name = serializer.validated_data["name"]
        description = serializer.validated_data["description"]
        user = request.user

        if Work.objects.filter(user=user, end_time__isnull=True).exists():
            if Work.objects.filter(
                user=user, end_time__isnull=True, object=object_id
            ).exists():
                return Response(
                    {"error": "Пользователь уже работает на этом объекте."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {"error": "Пользователь уже работает на другом объекте."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            obj = Object.objects.get(id=object_id)
            if user not in obj.worker.all() and user != obj.supervisor:
                return Response(
                    {"error": "Нет прав для работы с этим объектом"},
                    status=status.HTTP_403_FORBIDDEN,
                )
        except Object.DoesNotExist:
            return Response(
                {"error": "Объект не найден"}, status=status.HTTP_404_NOT_FOUND
            )

        work = Work.objects.create(object=obj, user=user)
        work.start_work(name, description)

        return Response(
            {"detail": "Работа успешно начата", "work_id": work.id},
            status=status.HTTP_201_CREATED,
        )


class EndWorkView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        security=[{"Bearer": []}],
        tags=["Work"],
        operation_description="Завершение работы на объекте",
        request_body=EndWorkSerializer,
        responses={
            200: "Работа успешно завершена",
            400: "Неверный запрос",
            403: "Доступ запрещен",
            404: "Работа не найдена",
        },
    )
    def post(self, request):
        serializer = EndWorkSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        work_id = serializer.validated_data["work_id"]
        work = Work.objects.get(id=work_id)

        work.end_work()
        return Response(
            {
                "detail": "Работа успешно завершена",
                "work_id": work.id,
                "end_time": work.end_time,
            },
            status=status.HTTP_200_OK,
        )



class ObjectStatusView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        security=[{"Bearer": []}],
        tags=["Object"],
        operation_description="Получение статуса работы пользователя с объектом",
        manual_parameters=[
            openapi.Parameter(
                "object_id",
                openapi.IN_PATH,
                description="ID объекта",
                type=openapi.TYPE_INTEGER,
            )
        ],
        responses={
            200: openapi.Response(
                description="Успешный ответ", schema=StatusResponseSerializer
            ),
            404: openapi.Response(description="Объект не найден"),
            403: openapi.Response(description="Доступ запрещен"),
        },
    )
    def get(self, request, object_id):
        user = request.user
        response_data = {"status": None, "stats": {}}

        try:
            obj = Object.objects.get(id=object_id)
        except Object.DoesNotExist:
            return Response({"status": "not_found"}, status=status.HTTP_404_NOT_FOUND)

        if user not in obj.worker.all() and user != obj.supervisor:
            return Response({"status": "forbidden"}, status=status.HTTP_403_FORBIDDEN)

        active_work = Work.objects.filter(user=user, end_time__isnull=True).first()

        total_completed = Work.objects.filter(
            object=obj, start_time__isnull=False, end_time__isnull=False
        ).count()

        user_completed = Work.objects.filter(
            object=obj, user=user, start_time__isnull=False, end_time__isnull=False
        ).count()

        response_data["stats"] = {
            "total_completed_works": total_completed,
            "user_completed_works": user_completed,
        }
        if active_work:
            if active_work.object_id != object_id:
                response_data.update(
                    {
                        "status": "busy",
                        "active_work": WorkSerializer(active_work).data,
                        "current_object": ObjectSerializer(active_work.object).data,
                    }
                )
            else:
                response_data.update(
                    {
                        "status": "work",
                        "object": ObjectSerializer(obj).data,
                        "work": WorkSerializer(active_work).data,
                        "available_actions": ["end"],
                    }
                )
        elif user.is_staff or user.is_superuser:
            response_data.update(
                {
                    "status": "review",
                    "object": ObjectSerializer(obj).data,
                    "available_actions": ["review"],
                }
            )
        else:
            response_data.update(
                {
                    "status": "start",
                    "object": ObjectSerializer(obj).data,
                    "available_actions": ["start"],
                }
            )

        return Response(response_data, status=status.HTTP_200_OK)

class WorkHistoryView(generics.ListAPIView):
    serializer_class = WorkWithReviewAndImagesSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        security=[{'Bearer': []}],
        tags=['Object'],
        operation_description='Получение истории работ пользователя на объекте с оценками и изображениями',
        manual_parameters=[
            openapi.Parameter(
                'object_id', openapi.IN_PATH, 
                description='ID объекта', 
                type=openapi.TYPE_INTEGER
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        object_id = self.kwargs['object_id']
        
        works = Work.objects.filter(object_id=object_id)
        if not works:
            return []
        
        for work in works:
            work.images = list(WorkImage.objects.filter(work_id=work.id).all())

        return works





# work images
class WorkImageUploadView(generics.CreateAPIView):
    serializer_class = WorkImageSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        security=[{"Bearer": []}],
        tags=["Work Images"],
        operation_description="Добавление изображения к работе",
        manual_parameters=[
            openapi.Parameter(
                "work_id",
                openapi.IN_PATH,
                description="ID работы",
                type=openapi.TYPE_INTEGER,
            )
        ],
        responses={
            201: WorkImageSerializer,
            400: "Ошибка валидации",
            403: "Доступ запрещен",
            404: "Работа не найдена",
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        work_id = self.kwargs["work_id"]
        try:
            work = Work.objects.get(
                id=work_id, user=self.request.user, end_time__isnull=True
            )
            serializer.save(work=work)
        except Work.DoesNotExist:
            raise serializers.ValidationError(
                "Работа не найдена или недоступна для добавления изображений"
            )


class WorkImageListView(generics.ListAPIView):
    serializer_class = WorkImageListSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        security=[{"Bearer": []}],
        tags=["Work Images"],
        operation_description="Получение списка изображений работы",
        manual_parameters=[
            openapi.Parameter(
                "work_id",
                openapi.IN_PATH,
                description="ID работы",
                type=openapi.TYPE_INTEGER,
            )
        ],
        responses={
            200: WorkImageListSerializer(many=True),
            403: "Доступ запрещен",
            404: "Работа не найдена",
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        work_id = self.kwargs["work_id"]
        work = Work.objects.get(id=work_id)

        if not (
            self.request.user.is_staff
            or self.request.user.is_superuser
            or work.user == self.request.user
        ):
            raise PermissionDenied()

        return WorkImage.objects.filter(work_id=work_id)


class WorkImageDetailView(generics.RetrieveAPIView):
    serializer_class = WorkImageSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        security=[{"Bearer": []}],
        tags=["Work Images"],
        operation_description="Получение информации об изображении",
        manual_parameters=[
            openapi.Parameter(
                "work_id",
                openapi.IN_PATH,
                description="ID работы",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "image_id",
                openapi.IN_PATH,
                description="ID изображения",
                type=openapi.TYPE_INTEGER,
            ),
        ],
        responses={200: WorkImageSerializer, 403: "Доступ запрещен", 404: "Не найдено"},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self):
        work_id = self.kwargs["work_id"]
        image_id = self.kwargs["image_id"]

        
        if WorkImage.objects.filter(id=image_id, work_id=work_id).exists():
            # print("EXISTS")
            work = Work.objects.get(id=work_id)
            image = WorkImage.objects.get(id=image_id, work_id=work_id)

            if not (
                self.request.user.is_staff
                or self.request.user.is_superuser
                or work.user == self.request.user
            ):
                raise PermissionDenied()

            return image
        raise NotFound()

class WorkImageDeleteView(generics.DestroyAPIView):
    queryset = WorkImage.objects.all()
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        security=[{"Bearer": []}],
        tags=["Work Images"],
        operation_description="Удаление изображения по его айди",
        operation_summary="Удаление изображения",
        manual_parameters=[
            openapi.Parameter(
                "work_id",
                openapi.IN_PATH,
                description="ID работы",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "image_id",
                openapi.IN_PATH,
                description="ID изображения",
                type=openapi.TYPE_INTEGER,
            ),
        ],
        responses={204: "Удалено", 403: "Доступ запрещен", 404: "Не найдено"},
    )
    
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def perform_destroy(self, instance):
        work = instance.work
        if work.end_time is not None or work.user != self.request.user:
            raise PermissionDenied("Нельзя удалять изображения завершенной работы")
        instance.delete()




class ReviewCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        security=[{"Bearer": []}],
        tags=["Review"],
        operation_summary="Оценка работы",
        request_body=ReviewSerializer,
        responses={200: "Оценка успешно оставлена", 400: "Ошибка валидации"},
    )
    def post(self, request, work_id):
        work = Work.objects.filter(id=work_id).first()
        
        if not work:
            return Response(
                {"error": "Работа не найдена."},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        if not request.user.is_staff and request.user:
            return Response(
                {"error": "Вы не можете оставить отзыв на эту работу."},
                status=status.HTTP_403_FORBIDDEN,
            )

        review_data = request.data
        review_data['work'] = work_id
        review_data['supervisor'] = request.user.id  
        
        serializer = ReviewSerializer(data=review_data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "Оценка успешно оставлена"},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class WorksWithoutReviewsView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        security=[{"Bearer": []}],
        tags=["Review"],
        operation_summary="Получить работы без отзывов",
        responses={200: "Список работ без отзывов", 404: "Работы не найдены"},
    )
    def get(self, request):
        if request.user.is_staff:
            works_without_reviews = Work.objects.filter(review__isnull=True)
            if not works_without_reviews:
                return Response({"error": "Работы без отзывов не найдены."}, status=404)
            
            serializer = WorkSerializer(works_without_reviews, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "У пользователя нет доступа к этому методу"}, status=status.HTTP_403_FORBIDDEN)
    
class UserWorksWithReviewsAndImagesView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        security=[{"Bearer": []}],
        tags=["Work"],
        operation_description="Получение всех работ пользователя с оценками и фотографиями",
        responses={200: "Список работ с оценками и фотографиями", 404: "Работы не найдены"},
    )
    def get(self, request):
        # Получаем все работы пользователя
        user = request.user
        works = Work.objects.filter(user=user)

        if not works:
            return Response({"error": "Работы не найдены."}, status=status.HTTP_404_NOT_FOUND)

        # Сериализуем работы с оценками и изображениями
        serializer = WorkWithReviewAndImagesSerializer(works, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserWorksWithReviewsAndImagesView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        security=[{"Bearer": []}],
        tags=["Work"],
        operation_description="Получение всех работ пользователя с оценками и фотографиями",
        responses={200: "Список работ с оценками и фотографиями", 404: "Работы не найдены"},
    )
    def get(self, request):
        user = request.user
        works = Work.objects.filter(user=user)
        if not works:
            return Response({"error": "Работы не найдены."}, status=status.HTTP_404_NOT_FOUND)
        
        for work in works:
            work.images = list(WorkImage.objects.filter(work_id=work.id).all())

        serializer = WorkWithReviewAndImagesSerializer(works, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class WorkDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        security=[{"Bearer": []}],
        tags=["Work"],
        operation_description="Получение работы пользователя с оценкой(ели имеется) и фотографией",
        responses={200: "работа с оценкой(если имеется) и фотографиями", 404: "Работы не найдены"},
    )

    def get(self, request, work_id):
        work = Work.objects.get(id=work_id)
        if work:
            work.images = list(WorkImage.objects.filter(work_id=work.id).all())
            serializer = WorkWithReviewAndImagesSerializer(work, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Работа не найдена"}, status=status.HTTP_404_NOT_FOUND)