from typing import Dict, Any

from django.http import Http404
from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import Serializer

from .models import Course, Lesson, CourseSubscription
from .permissions import CustomPermission
from .serializers import (
    CourseSerializer,
    LessonSerializer,
    SubscriptionCreateSerializer, SubscriptionDeleteSerializer
)


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

    def get_serializer_context(self) -> Dict[str, Any]:
        """
        Возвращает контекст для сериализатора.
        Добавляет текущего пользователя в контекст.

        :return: Контекст для сериализатора.
        """
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


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


class SubscriptionCreateView(generics.CreateAPIView):
    queryset = CourseSubscription.get_all_course_subscriptions()
    serializer_class = SubscriptionCreateSerializer


class SubscriptionDeleteView(generics.UpdateAPIView):
    queryset = CourseSubscription.get_all_course_subscriptions()
    serializer_class = SubscriptionDeleteSerializer
    http_method_names = ['put']

    def get_object(self):
        """
        Возвращает объект подписки, который будет обновлен при выполнении запроса.
        В данном случае, этот метод переопределен, чтобы получить объект подписки,
        который соответствует указанному курсу и текущему пользователю.
        Мы не передаем ID подписки в URL.
        Мы ищем подписку по переданному в теле запроса ID курса и
        по ID текущего пользователя. Такая подписка может быть только одна согласно
        реализации метода по созданию подписки.

        :return: Объект подписки.
        :raises Http404: Если подписка не найдена.
        """
        queryset = self.get_queryset()
        user = self.request.user
        course_id = self.request.data.get('course')
        obj = queryset.filter(user=user, course__id=course_id).first()

        if obj is None:
            raise Http404("Подписка не найдена.")

        return obj
