from django.apps import AppConfig
from pathlib import Path
import os


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    path = os.path.join(Path(__file__).resolve().parent.parent, 'core')
