from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
import pytz
from core.zoom_utils import create_zoom_meeting


class Command(BaseCommand):
    help = 'Test Zoom meeting creation'

    def handle(self, *args, **options):
        # Test Zoom meeting creation
        start_time = datetime.now(pytz.UTC) + timedelta(hours=1)
        url, error = create_zoom_meeting('Test Meeting', start_time, 30)
        self.stdout.write(f'URL: {url}')
        self.stdout.write(f'Error: {error}')
