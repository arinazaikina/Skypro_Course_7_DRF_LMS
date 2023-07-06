from typing import List

from django.contrib.auth.models import AbstractUser
from django.db import models

from app_course.models import Course, Lesson
from app_image.models import UserImage
from .managers import CustomUserManager

NULLABLE = {'blank': True, 'null': True}


class CustomUser(AbstractUser):
    """
    Модель, описывающая пользователя LMS-системы.
    Наследуется от AbstractUser.
    """
    objects = CustomUserManager()

    username = None
    email = models.EmailField(unique=True, verbose_name='Электронная почта')
    avatar = models.ForeignKey(UserImage, on_delete=models.SET_DEFAULT, default=1, related_name='users',
                               verbose_name='Аватар')
    phone = models.CharField(max_length=16, verbose_name='Телефон')
    city = models.CharField(max_length=100, verbose_name='Город')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        db_table = 'users'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    @classmethod
    def get_all_users(cls) -> List['CustomUser']:
        """
        Возвращает список всех пользователей
        """
        return cls.objects.all()


class Payment(models.Model):
    """Модель, описывающая платеж"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='payments', verbose_name='Пользователь')
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата оплаты')
    paid_course = models.ForeignKey(Course, on_delete=models.SET_NULL, **NULLABLE, verbose_name='Оплаченный курс')
    paid_lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, **NULLABLE, verbose_name='Оплаченный урок')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма оплаты')
    PAYMENT_METHODS = [
        ('cash', 'Наличные'),
        ('transfer', 'Перевод на счет'),
    ]
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='transfer',
                                      verbose_name='Способ оплаты')

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        db_table = 'payments'

    def __str__(self):
        return f"{self.user} - {self.payment_date}"

    @classmethod
    def get_all_payments(cls) -> List['Payment']:
        """
        Возвращает список всех платежей
        """
        return cls.objects.all()
