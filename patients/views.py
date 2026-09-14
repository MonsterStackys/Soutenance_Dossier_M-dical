from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from accounts.permissions import ReceptionMixin, StaffDossierMixin

from .forms import PatientForm, PatientSearchForm
from .models import Patient


class PatientListView(StaffDossierMixin, ListView):
    model = Patient
    template_name = "patients/patient_list.html"
    context_object_name = "patients"
    paginate_by = 12

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q", "").strip()
        if q:
            # icontains = on ignore majuscules / minuscules
            qs = qs.filter(
                Q(nom__icontains=q) | Q(prenom__icontains=q) | Q(numero_dossier__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["search_form"] = PatientSearchForm(self.request.GET)
        ctx["q"] = self.request.GET.get("q", "")
        return ctx


class PatientDetailView(StaffDossierMixin, DetailView):
    model = Patient
    template_name = "patients/patient_detail.html"
    context_object_name = "patient"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        patient = self.object
        ctx["constantes"] = patient.constantes.select_related("pris_par").all()[:8]
        ctx["consultations"] = patient.consultations.select_related("medecin", "constante").all()[:8]
        ctx["rendez_vous"] = patient.rendez_vous.select_related("medecin").all()[:8]
        return ctx


class PatientCreateView(ReceptionMixin, CreateView):
    model = Patient
    form_class = PatientForm
    template_name = "patients/patient_form.html"

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "Patient enregistré. Le numéro de dossier a été attribué.")
        return super().form_valid(form)


class PatientUpdateView(ReceptionMixin, UpdateView):
    model = Patient
    form_class = PatientForm
    template_name = "patients/patient_form.html"

    def form_valid(self, form):
        messages.success(self.request, "Dossier patient mis à jour.")
        return super().form_valid(form)


class PatientDeleteView(ReceptionMixin, DeleteView):
    model = Patient
    template_name = "patients/patient_confirm_delete.html"
    success_url = reverse_lazy("patients:liste")

    def form_valid(self, form):
        messages.warning(self.request, f"Le dossier {self.object.numero_dossier} a été supprimé.")
        return super().form_valid(form)
