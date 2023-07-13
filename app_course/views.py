from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import Serializer

from .models import Course, Lesson
from .permissions import CustomPermission
from .serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, CustomPermission]

    def get_queryset(self):
        """
        Возвращает курсы, которые должны быть отображены для текущего пользователя.

        Если пользователь является модератором (is_staff=True), возвращает все курсы.
        Если пользователь не является модератором, возвращает только те курсы,
        которые были созданы этим пользователем.
        """
        user = self.request.user

        if user.is_authenticated:
            if user.is_staff:
                return Course.get_all_courses()
            else:
                return Course.get_all_courses().filter(created_by=user)
        else:
            return Course.objects.none()

    def perform_create(self, serializer: Serializer) -> None:
        """
        Сохраняет новый объект при помощи сериализатора,
        устанавливая атрибут 'created_by' как текущий пользователь.

        :param serializer: Сериализатор для сохранения объекта.
        """
        serializer.save(created_by=self.request.user)


class LessonListCreateAPIView(generics.ListCreateAPIView):
    queryset = Lesson.get_all_lessons()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, CustomPermission]

    def get_queryset(self):
        """
        Возвращает уроки, которые должны быть отображены для текущего пользователя.

        Если пользователь является модератором (is_staff=True), возвращает все уроки.
        Если пользователь не является модератором, возвращает только те уроки,
        которые были созданы этим пользователем.
        """
        user = self.request.user

        if user.is_authenticated:
            if user.is_staff:
                return Lesson.get_all_lessons()
            else:
                return Lesson.get_all_lessons().filter(created_by=user)
        else:
            return Lesson.objects.none()

    def perform_create(self, serializer: Serializer) -> None:
        """
        Сохраняет новый объект при помощи сериализатора,
        устанавливая атрибут 'created_by' как текущий пользователь.

        :param serializer: Сериализатор для сохранения объекта.
        """
        serializer.save(created_by=self.request.user)


class LessonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.get_all_lessons()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, CustomPermission]
