# Petites fonctions pour écrire / masquer le journal d'audit.
from datetime import timedelta

from django.utils import timezone

from .models import AuditLog


def client_ip(request):
    # Derrière un proxy on a parfois X-Forwarded-For
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def enregistrer_audit(request, action, description=""):
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return None
    return AuditLog.objects.create(
        utilisateur=user,
        action=action,
        description=description or action,
        methode=request.method,
        chemin=request.path[:255],
        adresse_ip=client_ip(request),
    )


def masquer_commandes_expirees():
    # Plus de 24 h -> on renseigne efface_le, on ne supprime pas la ligne
    seuil = timezone.now() - timedelta(hours=24)
    return AuditLog.objects.filter(efface_le__isnull=True, created_at__lt=seuil).update(
        efface_le=timezone.now()
    )
