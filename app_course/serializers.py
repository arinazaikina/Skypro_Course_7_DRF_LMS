from typing import Dict, Any

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from app_image.models import CourseImage, LessonImage
from app_image.serializers import CourseImageSerializer, LessonImageSerializer
from .models import Course, Lesson, CourseSubscription
from .validators import YouTubeUrlValidator


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
    - created_by: ID и почта создателя урока (ссылка на модель CustomUser).

    Поле preview не является обязательным для заполнения.
    Поле name проверяется на уникальность.
    Поле video_url принимает только ссылки на YouTube.
    """
    preview = serializers.PrimaryKeyRelatedField(
        queryset=LessonImage.get_all_lesson_images(),
        required=False
    )

    name = serializers.CharField(
        validators=[UniqueValidator(queryset=Lesson.get_all_lessons())]
    )
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = ['id', 'name', 'description', 'preview', 'video_url', 'course', 'created_by']
        validators = [YouTubeUrlValidator(field='video_url')]

    def to_representation(self, instance: Lesson) -> Dict[str, Any]:
        """
        Преобразует экземпляр модели Lesson в словарь.
        Возвращает словарь с представлением урока.

        :param instance: Экземпляр модели Lesson.
        """
        lesson_output = super().to_representation(instance)
        lesson_output['preview'] = LessonImageSerializer(instance.preview).data
        return lesson_output

    @staticmethod
    def get_created_by(instance: Lesson) -> Dict[str, Any]:
        """
        Возвращает информацию о создателе урока (ID пользователя и почту).

        :param instance: Экземпляр модели Lesson.
        """
        created_by = instance.created_by
        return {
            'id': created_by.id,
            'email': created_by.email
        }


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
    - created_by: ID и почта создателя курса (ссылка на модель CustomUser).
    - subscribed: Флаг подписки текущего пользователя на курс.

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
    created_by = serializers.SerializerMethodField()
    subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'name', 'preview', 'description', 'lessons', 'lessons_count', 'created_by', 'subscribed']

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

    @staticmethod
    def get_created_by(instance: Course) -> Dict[str, Any]:
        """
        Возвращает информацию о создателе курса (ID пользователя и почту).

        :param instance: Экземпляр модели Course.
        """
        created_by = instance.created_by
        return {
            'id': created_by.id,
            'email': created_by.email
        }

    def get_subscribed(self, instance: Course) -> bool:
        """
        Возвращает флаг подписки текущего пользователя на курс.

        :param instance: Экземпляр модели Course.
        """
        request = self.context.get('request')
        user = request.user

        try:
            subscription = CourseSubscription.objects.get(user=user, course=instance)
            return subscription.subscribed
        except CourseSubscription.DoesNotExist:
            return False


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания подписки на курс.

    Поля:
    - course: ID курса, на который пользователь хочет подписаться.
    - subscribed: Флаг подписки (только для чтения).

    При попытке создать подписку, проверяет, есть ли уже подписка на данный курс у пользователя.
    Если подписка уже существует, возбуждает исключение.
    """
    subscribed = serializers.BooleanField(read_only=True)

    class Meta:
        model = CourseSubscription
        fields = ['course', 'subscribed']

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Проверяет, существует ли уже подписка на указанный курс у текущего пользователя.
        Если подписка уже есть, будет выброшено исключение.

        :param attrs: Входные данные сериализатора (ID курса, ID пользователя мы получим из запроса,
        так как пользователь авторизован).
        """
        user = self.context['request'].user
        course = attrs['course']
        subscription_exists = CourseSubscription.objects.filter(user=user, course=course, subscribed=True).exists()

        if subscription_exists:
            raise serializers.ValidationError(f"Подписка на данный курс у пользователя {user} уже существует.")

        return attrs

    def create(self, validated_data: Dict[str, Any]) -> CourseSubscription:
        """
        Создает подписку на курс.
        Возвращает созданный объект подписки.

        :param validated_data: Проверенные данные сериализатора.
        """
        user = self.context['request'].user
        course = validated_data['course']

        subscription, _ = CourseSubscription.objects.update_or_create(
            user=user,
            course=course,
            defaults={'subscribed': True}
        )

        return subscription

    def to_representation(self, instance: CourseSubscription) -> Dict[str, Any]:
        """
        Преобразует объект подписки в словарь с полной информацией
        и возвращает этот словарь.
        Информация будет отображена в ответе сервера.

        :param instance: Объект подписки.
        """
        rep = super().to_representation(instance)
        rep['user'] = {
            'id': instance.user.id,
            'username': instance.user.email
        }
        rep['course'] = {
            'id': instance.course.id,
            'name': instance.course.name
        }
        return rep


class SubscriptionDeleteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отмены подписки на курс.

    Поля:
    - course: ID курса, для которого пользователь хочет отменить подписку.
    - subscribed: Флаг подписки (только для чтения).

    При попытке отменить подписку, проверяет, не отменена ли уже эта подписка.
    Если подписка уже отменена, возбуждает исключение.
    Если такая подписка не найдена, возбуждает исключение.

    При успешной отмене подписки, обновляет флаг подписки на False.
    """
    subscribed = serializers.BooleanField(read_only=True)

    class Meta:
        model = CourseSubscription
        fields = ['course', 'subscribed']

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Проверяет, существует ли подписка на данный курс и не отменена ли она уже.
        Если подписка не существует или уже отменена, возбуждает исключение.

        Если подписка существует и активна, возвращает входные данные сериализатора.

        :param attrs: Входные данные сериализатора.
        """
        user = self.context['request'].user
        course = attrs['course']
        subscription = CourseSubscription.objects.filter(user=user, course=course).first()

        if not subscription:
            raise serializers.ValidationError("Подписка на этот курс не найдена.")
        elif not subscription.subscribed:
            raise serializers.ValidationError("Подписка на этот курс уже отменена.")

        return attrs

    def update(self, instance: CourseSubscription, validated_data: Dict[str, Any]) -> CourseSubscription:
        """
        Обновляет флаг подписки на False и сохраняет изменения.
        Возвращает обновленный объект подписки.

        :param instance: Объект подписки.
        :param validated_data: Проверенные данные сериализатора.
        """
        instance.subscribed = False
        instance.save()
        return instance

    def to_representation(self, instance: CourseSubscription) -> Dict[str, Any]:
        """
        Преобразует объект подписки в словарь с полной информацией
        и возвращает этот словарь.
        Информация будет отображена в ответе сервера.

        :param instance: Объект подписки.
        """
        response = super().to_representation(instance)
        response['user'] = {
            'id': instance.user.id,
            'username': instance.user.email,
        }
        response['course'] = {
            'id': instance.course.id,
            'name': instance.course.name,
        }
        return response
