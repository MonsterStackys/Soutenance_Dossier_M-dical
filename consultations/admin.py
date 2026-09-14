from django.contrib import admin

from .models import Constante, Consultation, LigneOrdonnance, Ordonnance, RendezVous


class LigneInline(admin.TabularInline):
    model = LigneOrdonnance
    extra = 1


@admin.register(Constante)
class ConstanteAdmin(admin.ModelAdmin):
    list_display = ("patient", "date", "tension_arterielle", "temperature", "pris_par")
    list_filter = ("date",)
    search_fields = ("patient__nom", "patient__numero_dossier")


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ("patient", "medecin", "motif", "date_consultation")
    list_filter = ("date_consultation",)
    search_fields = ("patient__nom", "diagnostic", "motif")


@admin.register(RendezVous)
class RendezVousAdmin(admin.ModelAdmin):
    list_display = ("patient", "medecin", "date_heure", "statut", "motif")
    list_filter = ("statut",)
    search_fields = ("patient__nom", "motif")


@admin.register(Ordonnance)
class OrdonnanceAdmin(admin.ModelAdmin):
    list_display = ("consultation", "date_creation")
    inlines = [LigneInline]
