from datetime import datetime, time, timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.utils import timezone
from django.views.generic import TemplateView

from consultations.models import Constante, Consultation, RendezVous
from patients.models import Patient
from accounts.models import AuditLog, User


class DashboardView(LoginRequiredMixin, TemplateView):
    # Même page pour tout le monde, le template cache/affiche selon le rôle

    template_name = "reports/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        aujourd_hui = timezone.localdate()
        debut = timezone.make_aware(datetime.combine(aujourd_hui, time.min))
        fin = debut + timedelta(days=1)

        consultations_qs = Consultation.objects.filter(
            date_consultation__gte=debut, date_consultation__lt=fin
        )
        ctx["consultations_du_jour"] = consultations_qs.count()
        ctx["constantes_du_jour"] = Constante.objects.filter(date__gte=debut, date__lt=fin).count()
        ctx["patients_total"] = Patient.objects.count()
        ctx["bar_total"] = max(ctx["patients_total"], 1)
        ctx["patients_recents"] = Patient.objects.order_by("-created_at")[:6]
        ctx["constantes_recentes"] = Constante.objects.select_related("patient", "pris_par")[:8]
        ctx["consultations_recentes"] = consultations_qs.select_related("patient", "medecin")[:8]

        genre_counts = Patient.objects.values("genre").annotate(n=Count("id"))
        ctx["nb_hommes"] = next((g["n"] for g in genre_counts if g["genre"] == "M"), 0)
        ctx["nb_femmes"] = next((g["n"] for g in genre_counts if g["genre"] == "F"), 0)

        today = aujourd_hui
        tranches = {"0-17": 0, "18-39": 0, "40-59": 0, "60+": 0}
        for p in Patient.objects.only("date_naissance"):
            age = today.year - p.date_naissance.year - (
                (today.month, today.day) < (p.date_naissance.month, p.date_naissance.day)
            )
            if age < 18:
                tranches["0-17"] += 1
            elif age < 40:
                tranches["18-39"] += 1
            elif age < 60:
                tranches["40-59"] += 1
            else:
                tranches["60+"] += 1
        ctx["tranches_age"] = tranches
        ctx["aujourdhui"] = aujourd_hui
        ctx["is_reception_home"] = self.request.user.role == "RECEPTIONNISTE"
        ctx["is_admin_home"] = self.request.user.is_admin()
        if self.request.user.is_admin():
            ctx["nb_utilisateurs"] = User.objects.count()
            ctx["audits_jour"] = AuditLog.objects.filter(efface_le__isnull=True)[:10]
            ctx["audits_jour_count"] = AuditLog.objects.filter(efface_le__isnull=True).count()
        if self.request.user.is_medecin():
            ctx["rdv_a_venir"] = RendezVous.objects.filter(
                date_heure__gte=timezone.now(), statut=RendezVous.Statut.PLANIFIE
            ).select_related("patient")[:8]
        return ctx
