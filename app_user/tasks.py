from datetime import datetime, timedelta

from celery import shared_task


def create_periodic_task() -> None:
    """
    Создает периодическую задачу для проверки и обновления статуса платежей.
    Если задача уже существует, она не будет создаваться повторно.
    """
    from django_celery_beat.models import IntervalSchedule, PeriodicTask
    interval, _ = IntervalSchedule.objects.get_or_create(every=5, period=IntervalSchedule.SECONDS)
    task_name = 'app_user.tasks.py.check_and_update_payment_status'
    task_description = 'Check and Update Payment Status'

    existing_task = PeriodicTask.objects.filter(name=task_description).first()

    if not existing_task:
        task = PeriodicTask.objects.create(
            interval=interval,
            name=task_description,
            task=task_name,
            enabled=True,
            start_time=datetime.now() + timedelta(seconds=5)
        )
        task.save()


@shared_task
def check_and_update_payment_status() -> None:
    """
    Проверяет и обновляет статус неподтвержденных платежей.

    Использует модель Payment для получения неподтвержденных платежей,
    у которых есть указанные ID метода платежа и намерения платежа.
    Затем вызывает метод StripeService.confirm_payment() для каждого платежа,
    чтобы подтвердить его.
    """
    from .models import Payment
    from .services import StripeService
    unconfirmed_payments = Payment.objects.filter(is_confirmed=False,
                                                  payment_method_id__isnull=False,
                                                  payment_intent_id__isnull=False)
    for payment in unconfirmed_payments:
        StripeService.confirm_payment(payment_intent_id=payment.payment_intent_id)
