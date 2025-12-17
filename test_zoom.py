import os
import sys
import django
from datetime import datetime, timedelta
import pytz

# Add the project root and Django project directory to the Python path
sys.path.insert(0, 'c:/Users/manas/OneDrive/Dokumen/aihealth')
sys.path.insert(0, 'c:/Users/manas/OneDrive/Dokumen/aihealth/ai_driven_mental_psychological_system')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_driven_mental_psychological_system.settings')

# Setup Django
django.setup()

from core.zoom_utils import create_zoom_meeting

# Test Zoom meeting creation
start_time = datetime.now(pytz.UTC) + timedelta(hours=1)
url, error = create_zoom_meeting('Test Meeting', start_time, 30)
print('URL:', url)
print('Error:', error)
