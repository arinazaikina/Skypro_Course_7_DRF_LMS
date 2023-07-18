from django.apps import AppConfig

from .tasks import create_periodic_task


class AppUserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_user'
    verbose_name = 'Пользователи'

    def ready(self):
        """
        При запуске приложения создаёт периодическую задачу
        на проверку статуса платежей, если она еще не создана.
        """
        create_periodic_task()
