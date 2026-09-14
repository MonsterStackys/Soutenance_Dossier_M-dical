from django.contrib import admin

from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("numero_dossier", "nom", "prenom", "date_naissance", "genre", "telephone")
    search_fields = ("numero_dossier", "nom", "prenom", "telephone")
    list_filter = ("genre", "groupe_sanguin")
    readonly_fields = ("numero_dossier", "created_at", "updated_at")
