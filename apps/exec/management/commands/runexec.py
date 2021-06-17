from django.core.management.base import BaseCommand
from apps.exec.scheduler import Task


class Command(BaseCommand):
    help = 'Start monitor process'

    def handle(self, *args, **options):
        data = Task()
        data.run()
