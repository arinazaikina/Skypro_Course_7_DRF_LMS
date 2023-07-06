from rest_framework import viewsets, generics

from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Course"""
    queryset = Course.get_all_courses()
    serializer_class = CourseSerializer


class LessonListCreateAPIView(generics.ListCreateAPIView):
    """Обобщенное представление для списка и создания уроков"""
    queryset = Lesson.get_all_lessons()
    serializer_class = LessonSerializer


class LessonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Обобщенное представление для получения, обновления и удаления уроков"""
    queryset = Lesson.get_all_lessons()
    serializer_class = LessonSerializer
