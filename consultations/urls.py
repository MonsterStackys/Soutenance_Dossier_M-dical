from django.urls import path

from .views import (
    ConstanteCreateView,
    ConsultationCreateView,
    ConsultationDetailView,
    OrdonnancePrintView,
    OrdonnanceUpdateView,
    RendezVousCreateView,
    RendezVousListView,
    RendezVousUpdateView,
)

app_name = "consultations"

urlpatterns = [
    # rendez-vous avant <pk> sinon Django croirait que "rendez-vous" est un numéro
    path("rendez-vous/", RendezVousListView.as_view(), name="rdv_liste"),
    path("rendez-vous/nouveau/", RendezVousCreateView.as_view(), name="rdv_creer"),
    path(
        "patients/<int:patient_pk>/rendez-vous/nouveau/",
        RendezVousCreateView.as_view(),
        name="rdv_creer_patient",
    ),
    path("rendez-vous/<int:pk>/modifier/", RendezVousUpdateView.as_view(), name="rdv_modifier"),
    path(
        "patients/<int:patient_pk>/constantes/nouvelle/",
        ConstanteCreateView.as_view(),
        name="constante_creer",
    ),
    path(
        "patients/<int:patient_pk>/nouvelle/",
        ConsultationCreateView.as_view(),
        name="creer",
    ),
    path("<int:pk>/", ConsultationDetailView.as_view(), name="detail"),
    path("<int:pk>/ordonnance/", OrdonnanceUpdateView.as_view(), name="ordonnance"),
    path("<int:pk>/ordonnance/imprimer/", OrdonnancePrintView.as_view(), name="ordonnance_imprimer"),
]
