import os
import sys
# Path to your virtual environment
venv_path = '/home/ubuntu/kriangle/venv'

# Add the virtual environment's site-packages to sys.path
sys.path.insert(0, os.path.join(venv_path, 'lib', 'python3.12', 'site-packages'))

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kriangle.settings')

# Import the application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
