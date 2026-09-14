# Réglages du projet. Pour un poste local on reste simple : SQLite + DEBUG.
from pathlib import Path

from django.contrib.messages import constants as message_constants

# Dossier racine du projet (celui qui contient manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent

# Clé de démo — à changer si un jour on met ça en ligne
SECRET_KEY = "django-insecure-health-centre-licence-demo-change-me"

DEBUG = True  # pratique en soutenance, à couper en production

# * = on peut ouvrir l'app depuis un autre PC du réseau local
ALLOWED_HOSTS = ["*"]

NOM_STRUCTURE = "Poste de Santé Khar Yalla"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # nos 4 applis métier
    "accounts",
    "patients",
    "consultations",
    "reports",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",  # token anti-CSRF sur les POST
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "accounts.middleware.AuditMiddleware",  # journal des actions
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "health_centre.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # templates globaux (base.html, login, etc.)
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.media",
                "accounts.context_processors.role_flags",
                "accounts.context_processors.structure",
            ],
        },
    },
]

WSGI_APPLICATION = "health_centre.wsgi.application"

# Un seul fichier .sqlite3, facile à copier pour sauvegarder
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Obligatoire dès qu'on étend AbstractUser (avant la 1re migrate)
AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Africa/Abidjan"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Photos de profil
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "reports:dashboard"
LOGOUT_REDIRECT_URL = "accounts:login"

# Session ~ une vacation (8 h)
SESSION_COOKIE_AGE = 60 * 60 * 8
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
# Si on ouvre l'app en http://192.168.x.x:8000, il faudra ajouter cette origine ici
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# Pour que les messages Django collent aux classes Bootstrap (error -> danger)
MESSAGE_TAGS = {
    message_constants.DEBUG: "secondary",
    message_constants.INFO: "info",
    message_constants.SUCCESS: "success",
    message_constants.WARNING: "warning",
    message_constants.ERROR: "danger",
}
