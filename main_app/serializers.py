
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Object, Work, Review, WorkImage


class ObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Object
        fields = ['id', 'name', 'address', 'task_description', 'deadline', 'status', 'worker', 'supervisor']

class WorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Work
        fields = ['object', 'user', 'start_time', 'end_time']

class StartWorkSerializer(serializers.Serializer):
    object = serializers.IntegerField(
        required=True,
        help_text="ID объекта для начала работы",
        min_value=1  # Гарантируем положительный ID
    )

    def validate_object(self, value):
        """Проверяем существование объекта"""
        if not Object.objects.filter(id=value).exists():
            raise serializers.ValidationError("Объект с таким ID не существует")
        return value
    
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