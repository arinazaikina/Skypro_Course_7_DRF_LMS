import logging
from datetime import datetime
from typing import Dict, Any

from django.http import Http404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import Serializer

from .models import Course, Lesson, CourseSubscription
from .paginations import Pagination
from .permissions import CustomPermission
from .serializers import (
    CourseSerializer,
    LessonSerializer,
    SubscriptionCreateSerializer,
    SubscriptionDeleteSerializer
)
from .tasks import was_updated_recently, send_course_update_notifications, send_lesson_update_notifications

logger = logging.getLogger(__name__)


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, CustomPermission]
    pagination_class = Pagination

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description='Номер страницы',
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={200: CourseSerializer(many=True)}
    )
    def list(self, request):
        return super().list(request)

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
                return Course.get_all_courses().order_by('id')
            else:
                return Course.get_all_courses().filter(created_by=user).order_by('id')
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

    def perform_update(self, serializer: Serializer) -> None:
        """
        Обновляет объект курса и отправляет уведомление об обновлении подписчикам курса,
        если после последнего обновления курса прошло 60 секунд и больше.

        :param serializer: Сериализатор для сохранения объекта.
        """
        instance = self.get_object()
        last_course_update = instance.updated_at
        instance = serializer.save()
        if not was_updated_recently(last_course_update):
            send_course_update_notifications.delay(instance.id)


class LessonListCreateAPIView(generics.ListCreateAPIView):
    queryset = Lesson.get_all_lessons()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, CustomPermission]
    pagination_class = Pagination

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description='Номер страницы',
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={200: LessonSerializer(many=True)}
    )
    def list(self, request):
        return super().list(request)

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
                return Lesson.get_all_lessons().order_by('id')
            else:
                return Lesson.get_all_lessons().filter(created_by=user).order_by('id')
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

    def perform_update(self, serializer: Serializer) -> None:
        """
        Обновляет объект урока и отправляет уведомление подписчикам курса, в который
        входит этот урок, если после последнего обновления курса прошло 60 секунд и больше.
        При обновлении урока, также обновляется и время последнего обновления курса.

        :param serializer: Сериализатор для сохранения объекта.
        """
        instance = self.get_object()
        last_course_update = instance.course.updated_at
        instance = serializer.save()
        instance.course.update_at = datetime.now()
        instance.course.save()
        if not was_updated_recently(last_course_update):
            send_lesson_update_notifications.delay(instance.id)


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
