from rest_framework import serializers

from .models import LessonImage, CourseImage, UserImage


class LessonImageSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели LessonImage.

    Поля:
    - id: Целочисленный идентификатор изображения урока.
    - image: Изображение урока.
    """
    class Meta:
        model = LessonImage
        fields = '__all__'


class CourseImageSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели CourseImage.

    Поля:
    - id: Целочисленный идентификатор изображения курса.
    - image: Изображение курса.
    """
    class Meta:
        model = CourseImage
        fields = '__all__'


class UserImageSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели UserImage.

    Поля:
    - id: Целочисленный идентификатор изображения пользователя.
    - image: Изображение пользователя.
    """
    class Meta:
        model = UserImage
        fields = '__all__'
