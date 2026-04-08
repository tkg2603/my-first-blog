"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['SECRET_KEY'] = 'j1#8ne%4^&!zeygq0!23l-nou)'
os.environ['DEBUG'] = 'True' 

application = get_wsgi_application()
