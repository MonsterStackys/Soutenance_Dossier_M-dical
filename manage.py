#!/usr/bin/env python
# C'est le fichier qu'on lance : python manage.py runserver (ou migrate, etc.)
import os
import sys


def main():
    # On dit à Django où se trouvent les réglages du projet
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "health_centre.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # En général c'est que le venv n'est pas activé / Django pas installé
        raise ImportError(
            "Django n'est pas installé. Active le venv puis : pip install -r requirements.txt"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
