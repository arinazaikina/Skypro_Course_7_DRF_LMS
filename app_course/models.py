from typing import List, Optional

from django.db import models

from app_image.models import CourseImage, LessonImage


class Course(models.Model):
    """
    Модель, описывающая курс.
    """
    name = models.CharField(max_length=255, verbose_name='Название')
    preview = models.ForeignKey(CourseImage, on_delete=models.SET_DEFAULT, default=1, related_name='courses',
                                verbose_name='Превью')
    description = models.TextField(verbose_name='Описание')
    created_by = models.ForeignKey('app_user.CustomUser', on_delete=models.CASCADE,
                                   verbose_name='Создано пользователем')
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=50000, verbose_name='Стоимость курса')

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        db_table = 'courses'

    def __str__(self):
        return f'{self.name}'

    @classmethod
    def get_all_courses(cls) -> List['Course']:
        """
        Возвращает список всех курсов
        """
        return cls.objects.all()

    @classmethod
    def get_by_id(cls, course_id: int) -> Optional['Course']:
        """
        Возвращает курс по его идентификатору
        """
        try:
            return cls.objects.get(id=course_id)
        except cls.DoesNotExist:
            return None


class Lesson(models.Model):
    """
    Модель, описывающая урок.
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons', verbose_name='Курс')
    name = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    preview = models.ForeignKey(LessonImage, on_delete=models.SET_DEFAULT, default=1, related_name='lessons',
                                verbose_name='Превью')
    video_url = models.URLField(verbose_name='Ссылка на видео')
    created_by = models.ForeignKey('app_user.CustomUser', on_delete=models.CASCADE,
                                   verbose_name='Создано пользователем')

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        db_table = 'lessons'

    def __str__(self):
        return f'{self.name}'

    @classmethod
    def get_all_lessons(cls) -> List['Lesson']:
        """
        Возвращает список всех уроков
        """
        return cls.objects.all()


class CourseSubscription(models.Model):
    """
    Модель, описывающая подписку пользователя на курс.
    """
    user = models.ForeignKey('app_user.CustomUser', on_delete=models.CASCADE, verbose_name='Пользователь')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='Курс')
    subscribed = models.BooleanField(default=False, verbose_name='Статус подписки')

    class Meta:
        unique_together = ('user', 'course')
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        db_table = 'course_subscriptions'

    def __str__(self):
        return f'{self.user} {self.course.name} {self.subscribed}'

    @classmethod
    def get_all_course_subscriptions(cls) -> List['Lesson']:
        """
        Возвращает список всех подписок на курс
        """
        return cls.objects.all()
