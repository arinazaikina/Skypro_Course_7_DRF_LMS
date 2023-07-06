from typing import List

from django.db import models


class LessonImage(models.Model):
    """Модель, описывающая изображения урока"""
    image = models.ImageField(upload_to='lessons/', default='lessons/default.png', verbose_name='Изображение урока')

    class Meta:
        verbose_name = 'Изображение урока'
        verbose_name_plural = 'Изображения уроков'
        db_table = 'lesson_images'

    def __str__(self):
        return f'{self.image}'

    @classmethod
    def get_all_lesson_images(cls) -> List['LessonImage']:
        """
        Возвращает список всех изображений уроков
        """
        return cls.objects.all()


class CourseImage(models.Model):
    """Модель, описывающая изображения курса"""
    image = models.ImageField(upload_to='courses/', default='courses/default.png', verbose_name='Изображение курса')

    class Meta:
        verbose_name = 'Изображение курса'
        verbose_name_plural = 'Изображения курсов'
        db_table = 'courses_images'

    def __str__(self):
        return f'{self.image}'

    @classmethod
    def get_all_course_images(cls) -> List['CourseImage']:
        """
        Возвращает список всех изображений курсов
        """
        return cls.objects.all()


class UserImage(models.Model):
    """Модель, описывающая изображения пользователя"""
    image = models.ImageField(upload_to='users/', default='users/default.png', verbose_name='Изображение пользователя')

    class Meta:
        verbose_name = 'Изображение пользователя'
        verbose_name_plural = 'Изображения пользователей'
        db_table = 'user_images'

    def __str__(self):
        return f'{self.image}'

    @classmethod
    def get_all_user_images(cls) -> List['UserImage']:
        """
        Возвращает список всех изображений пользователей
        """
        return cls.objects.all()
