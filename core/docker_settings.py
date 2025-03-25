import os
from pathlib import Path

# Configuration for handling static files in Docker
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Ensure static files are served correctly
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'