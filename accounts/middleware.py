# Passe sur chaque requête : d'abord on masque le trop vieux, ensuite on log les POST.
from django.conf import settings

from accounts.audit import enregistrer_audit, masquer_commandes_expirees


class AuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        masquer_commandes_expirees()
        response = self.get_response(request)
        self._journaliser(request, response)
        return response

    def _journaliser(self, request, response):
        # On ne note que les actions (POST) qui ont marché
        if request.method != "POST":
            return
        if not (200 <= response.status_code < 400):
            return
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return
        path = request.path
        static = getattr(settings, "STATIC_URL", "/static/") or "/static/"
        media = getattr(settings, "MEDIA_URL", "/media/") or "/media/"
        if path.startswith(static) or path.startswith(media):
            return
        if path.startswith("/admin/jsi18n"):
            return
        match = getattr(request, "resolver_match", None)
        vue = f"{match.app_name}:{match.url_name}" if match else path
        enregistrer_audit(request, action=vue, description=f"{request.method} {path}")
