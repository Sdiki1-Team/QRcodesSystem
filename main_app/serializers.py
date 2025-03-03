
from email.policy import default
from urllib import request
from pkg_resources import require
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied 
from django.contrib.auth import authenticate
from django.conf import settings

from auth_app.models import CustomUser
from .models import Object, Work, Review, WorkImage


class ObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Object
        fields = ['id', 'name', 'address', 'task_description', 'deadline', 'worker', 'supervisor']

class ObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Object
        fields = ['id', 'name', 'address', 'task_description', 'deadline', 'start_time', 'end_time']

class WorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Work
        fields = ['id', 'name', 'description', 'worker_comment', 'user', 'start_time', 'end_time']

class ObjectStatsSerializer(serializers.Serializer):
    total_completed_works = serializers.IntegerField()
    user_completed_works = serializers.IntegerField()

class StatusResponseSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['busy', 'start', 'work', 'review', 'not_found', 'forbidden'])
    object = ObjectSerializer(required=False)
    work = WorkSerializer(required=False)
    available_actions = serializers.ListField(
        child=serializers.ChoiceField(choices=['start', 'end', 'review']), 
        required=False
    )
    stats = ObjectStatsSerializer()

class WorkHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Work
        fields = ['id', 'name', 'description', 'start_time', 'end_time', 'user']
    
class StartWorkSerializer(serializers.Serializer):
    object = serializers.IntegerField(
        required=True,
        help_text="ID объекта для начала работы",
        min_value=1 
    )
    name = serializers.CharField(
        required=True,
        help_text="Название выполняемой работы"
    )
    description = serializers.CharField(
        required=False,
        help_text="Описание выполняемой работы"
    )

    def validate_object(self, value):
        """Проверяем существование объекта"""
        if not Object.objects.filter(id=value).exists():
            raise serializers.ValidationError("Объект с таким ID не существует")
        return value
    

class StartFreeWorkSerializer(serializers.Serializer):
    work_id = serializers.IntegerField(
        required=True,
        help_text="ID работы для начала работы",
        min_value=1
    )

    def validate_object(self, value):
        """Проверяем существование работы"""
        if not Work.objects.filter(id=value, time_start=None).exists():
            raise serializers.ValidationError("Работы с таким ID не существует или уже начата")
        return value
    

class EndWorkSerializer(serializers.Serializer):
    work_id = serializers.IntegerField(
        required=True,
        min_value=1,
        help_text="ID работы для завершения"
    )
    comment = serializers.CharField(
        required=False,
        null=True,
        help_text="Комментарий от работника"
    )
    def validate_work_id(self, value):
        """Проверяем существование работы и права доступа"""
        try:
            work = Work.objects.get(id=value)
            if work.user != self.context['request'].user:
                raise PermissionDenied("Нет прав для завершения этой работы")
            if work.end_time is not None:
                raise serializers.ValidationError("Работа уже завершена")
            return value
        except Work.DoesNotExist:
            raise serializers.ValidationError("Работа не найдена")
        
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['work', 'supervisor', 'rating', 'comment', 'review_date']


class WorkImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkImage
        fields = ('id', 'image', 'uploaded_at', 'work')
        read_only_fields = ('work', 'uploaded_at')
        extra_kwargs = {
            'image': {'required': True}
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['image'] = "/media/" + instance.image.url.replace(settings.MEDIA_URL, '', 1)
        return representation
    

class WorkImageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkImage
        fields = ('id', 'image', 'uploaded_at', 'work')
        read_only_fields = ('work', 'uploaded_at')
        extra_kwargs = {
            'image': {'required': True}
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.image:
            representation['image'] = "/media/" + instance.image.url.replace(settings.MEDIA_URL, '', 1)
        else:
            representation['image'] = None 
        return representation
    
class ReviewSerializer2(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['rating', 'comment', 'review_date']

class WorkImageListSerializer2(serializers.ModelSerializer):
    class Meta:
        model = WorkImage
        fields = ('id', 'uploaded_at', 'image')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.image:
            representation['image'] = "/media/" + instance.image.url.replace(settings.MEDIA_URL, '', 1)
        else:
            representation['image'] = None 
        return representation

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CustomUser
        fields = ['id', 'fullname', 'username']

class WorkWithReviewAndImagesSerializer(serializers.ModelSerializer):
    review = ReviewSerializer2(read_only=True, required=False)
    images = WorkImageListSerializer2(many=True, read_only=True, required=False, default=[])
    object = ObjectSerializer(many=False, required=False)
    user = UserSerializer(many=False, default={}, required=False)

    class Meta:
        model = Work
        fields = ['id', 'object', 'name',  'description', 'worker_comment', 'user', 'start_time', 'end_time', 'review', 'images']


class WorkFreeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Work
        fields = ['id', 'name', 'description']


class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CustomUser
        fields = ['id', 'fullname', 'username']



class WorkSerializer2(serializers.ModelSerializer):
    
    images = WorkImageListSerializer2(many=True, read_only=True, required=False, default=[])
    object = ObjectSerializer(many=False, required=False)
    
    class Meta:
        model = Work
        fields = ['id', 'name', 'description', 'worker_comment', 'user', 'start_time', 'end_time', 'images', 'object']
