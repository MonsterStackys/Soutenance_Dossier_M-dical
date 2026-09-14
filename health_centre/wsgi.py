# Utilisé par un serveur type Gunicorn. En local on passe plutôt par manage.py runserver.
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "health_centre.settings")

application = get_wsgi_application()
