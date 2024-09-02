from django.core.management.base import BaseCommand
from django.core.management import call_command
from core.models import Book


class Command(BaseCommand):
    help = 'Load initial data if not already present in the database.'

    def handle(self, *args, **kwargs):
        if not Book.objects.exists():
            self.stdout.write(self.style.NOTICE('Loading initial data...'))
            call_command('loaddata', 'initial_data.json')
            self.stdout.write(self.style.SUCCESS('Initial data loaded successfully.'))
        else:
            self.stdout.write(self.style.SUCCESS('Initial data already present in the database.'))