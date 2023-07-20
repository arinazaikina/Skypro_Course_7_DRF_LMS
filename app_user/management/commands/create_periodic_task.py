from django.core.management.base import BaseCommand

from app_user.tasks import create_periodic_task


class Command(BaseCommand):
    help = 'Create periodic task'

    def handle(self, *args, **options):
        create_periodic_task()
