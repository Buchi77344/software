from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Runs the Django development server on 0.0.0.0:8000'

    def handle(self, *args, **kwargs):
        call_command('runserver', '0.0.0.0:8000')
