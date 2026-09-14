"""
Script autonome équivalent à : python manage.py seed_data
Usage : python populate_db.py
"""
import os
import sys

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "health_centre.settings")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.core.management import call_command

if __name__ == "__main__":
    call_command("seed_data")
