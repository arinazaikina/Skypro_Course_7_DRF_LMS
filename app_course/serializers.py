from typing import Dict, Any

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from app_image.models import CourseImage, LessonImage
from app_image.serializers import CourseImageSerializer, LessonImageSerializer
from .models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Lesson.

    Поля:
    - id: Целочисленный идентификатор урока.
    - name: Строка с именем урока.
    - description: Строка с описанием урока.
    - preview: Идентификатор превью урока (ссылка на модель LessonImage).
    - video_url: Строка с URL-адресом видео урока.
    - course: Идентификатор курса, к которому принадлежит урок.

    Поле preview не является обязательным для заполнения.

    Поле name проверяется на уникальность.
    """
    preview = serializers.PrimaryKeyRelatedField(
        queryset=LessonImage.get_all_lesson_images(),
        required=False
    )

    name = serializers.CharField(
        validators=[UniqueValidator(queryset=Lesson.get_all_lessons())]
    )

    class Meta:
        model = Lesson
        fields = ['id', 'name', 'description', 'preview', 'video_url', 'course']

    def to_representation(self, instance: Lesson) -> Dict[str, Any]:
        """
        Преобразует экземпляр модели Lesson в словарь.
        Возвращает словарь с представлением урока.

        :param instance: Экземпляр модели Lesson.
        """
        lesson_output = super().to_representation(instance)
        lesson_output['preview'] = LessonImageSerializer(instance.preview).data
        return lesson_output


class CourseSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Course.

    Поля:
    - id: Целочисленный идентификатор курса.
    - name: Строка с именем курса.
    - preview: Идентификатор превью курса (ссылка на модель CourseImage).
    - description: Строка с описанием курса.
    - lessons: Список уроков, относящихся к курсу (ссылки на модель Lesson).
    - lessons_count: Количество уроков в курсе.

    Поле preview не является обязательным для заполнения.

    Поле name проверяется на уникальность.
    """
    preview = serializers.PrimaryKeyRelatedField(
        queryset=CourseImage.get_all_course_images(),
        required=False
    )
    name = serializers.CharField(
        validators=[UniqueValidator(queryset=Course.get_all_courses())]
    )
    lessons = LessonSerializer(many=True, read_only=True)
    lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'name', 'preview', 'description', 'lessons', 'lessons_count']

    def to_representation(self, instance: Course) -> Dict[str, Any]:
        """
        Преобразует экземпляр модели Course в словарь.
        Возвращает словарь с представлением курса.

        :param instance: Экземпляр модели Course.
        """
        course_output = super().to_representation(instance)
        course_output['preview'] = CourseImageSerializer(instance.preview).data
        return course_output

    @staticmethod
    def get_lessons_count(instance: Course) -> int:
        """
        Возвращает количество уроков в курсе.

        :param instance: Экземпляр модели Course.
        """
        return instance.lessons.count()
