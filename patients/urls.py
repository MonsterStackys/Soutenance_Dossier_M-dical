from django.urls import path

from .views import (
    PatientCreateView,
    PatientDeleteView,
    PatientDetailView,
    PatientListView,
    PatientUpdateView,
)

app_name = "patients"

urlpatterns = [
    path("", PatientListView.as_view(), name="liste"),
    path("nouveau/", PatientCreateView.as_view(), name="creer"),
    path("<int:pk>/", PatientDetailView.as_view(), name="detail"),
    path("<int:pk>/modifier/", PatientUpdateView.as_view(), name="modifier"),
    path("<int:pk>/supprimer/", PatientDeleteView.as_view(), name="supprimer"),
]
