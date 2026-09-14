# Routes principales. Chaque appli a ensuite son propre urls.py.
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("comptes/", include("accounts.urls")),
    path("patients/", include("patients.urls")),
    path("consultations/", include("consultations.urls")),
    path("", include("reports.urls")),  # l'accueil = tableau de bord
    path("favicon.ico", RedirectView.as_view(url="/static/img/favicon.svg", permanent=False)),
]

# page 403.html à la racine des templates
handler403 = "django.views.defaults.permission_denied"

admin.site.site_header = "Poste de Santé Khar Yalla — Administration"
admin.site.site_title = "Khar Yalla"
admin.site.index_title = "Gestion interne"

# En DEBUG, Django sert lui-même les photos uploadées
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
