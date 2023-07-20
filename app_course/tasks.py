import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import Course, Lesson

logger = logging.getLogger(__name__)


def was_updated_recently(last_update: timezone.datetime) -> bool:
    """
    Проверяет, был ли объект обновлен недавно.
    True, если объект был обновлен менее 60 секунд назад, иначе False.

    :param last_update: Время последнего обновления.
    """
    now = timezone.now()
    diff = now - last_update
    logger.info(f'Курс был обновлен {diff} сек назад')
    return diff.total_seconds() < 60


@shared_task
def send_course_update_notifications(course_id: int) -> None:
    """
    Отправляет уведомления об обновлении курса подписчикам.

    :param course_id: Идентификатор курса.
    """
    course = Course.get_by_id(course_id)
    if course is not None:
        subscribers = course.subscriptions.filter(subscribed=True)
        for subscription in subscribers:
            try:
                logger.info(f'Отправка письма для {subscribers}')
                send_mail(
                    subject='Обновление курса',
                    message=f'Курс "{course.name}" был обновлен.',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[subscription.user.email],
                )
            except Exception as error:
                logger.error(f'Ошибка отправки письма: {error}')


@shared_task
def send_lesson_update_notifications(lesson_id: int) -> None:
    """
    Отправляет уведомления об обновлении урока подписчикам курса, в который входит этот урок.

    :param lesson_id: Идентификатор урока.
    """
    lesson = Lesson.get_by_id(lesson_id)
    if lesson is not None:
        subscribers = lesson.course.subscriptions.filter(subscribed=True)
        for subscription in subscribers:
            try:
                logger.info(f'Отправка письма для {subscribers}')
                send_mail(
                    subject='Обновление урока',
                    message=f'Урок "{lesson.name}" был обновлен.',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[subscription.user.email],
                )
            except Exception as error:
                logger.error(f'Ошибка отправки письма: {error}')
