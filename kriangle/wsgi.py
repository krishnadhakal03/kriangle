"""
WSGI config for kriangle project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
import sys

# Add virtual environment to sys.path
activate_this = '/home/ubuntu/kriangle/venv/bin/activate_this.py'
exec(open(activate_this).read(), {'__file__': activate_this})

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kriangle.settings')

application = get_wsgi_application()
