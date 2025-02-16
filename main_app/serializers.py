
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Object, Work, Review


class ObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Object
        fields = ['id', 'name', 'address', 'task_description', 'deadline', 'status', 'worker', 'supervisor']

# Сериализатор для работы
class WorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Work
        fields = ['object', 'user', 'start_time', 'end_time']

# Сериализатор для отзыва
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['work', 'supervisor', 'rating', 'comment', 'review_date']