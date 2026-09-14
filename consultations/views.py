from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, TemplateView, UpdateView

from accounts.permissions import InfirmierMixin, MedecinMixin, SoignantMixin
from patients.models import Patient

from .forms import ConstanteForm, ConsultationForm, LigneOrdonnanceFormSet, RendezVousForm
from .models import Constante, Consultation, Ordonnance, RendezVous


class PatientKwargMixin:
    def get_patient(self):
        return get_object_or_404(Patient, pk=self.kwargs["patient_pk"])


class ConstanteCreateView(InfirmierMixin, PatientKwargMixin, CreateView):
    model = Constante
    form_class = ConstanteForm
    template_name = "consultations/constante_form.html"

    def get_success_url(self):
        return reverse("patients:detail", kwargs={"pk": self.object.patient_id})

    def form_valid(self, form):
        form.instance.patient = self.get_patient()
        form.instance.pris_par = self.request.user
        messages.success(self.request, "Constantes enregistrées.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["patient"] = self.get_patient()
        return ctx


class ConsultationCreateView(SoignantMixin, PatientKwargMixin, CreateView):
    # Infirmier et médecin peuvent consulter. L'ordonnance, c'est le médecin.

    model = Consultation
    form_class = ConsultationForm
    template_name = "consultations/consultation_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["patient"] = self.get_patient()
        return kwargs

    def form_valid(self, form):
        form.instance.patient = self.get_patient()
        form.instance.medecin = self.request.user
        if self.request.user.is_medecin():
            messages.success(self.request, "Consultation enregistrée. Vous pouvez rédiger l'ordonnance.")
        else:
            messages.success(self.request, "Consultation enregistrée.")
        return super().form_valid(form)

    def get_success_url(self):
        if self.request.user.is_medecin():
            return reverse("consultations:ordonnance", kwargs={"pk": self.object.pk})
        return reverse("consultations:detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["patient"] = self.get_patient()
        return ctx


class ConsultationDetailView(SoignantMixin, DetailView):
    model = Consultation
    template_name = "consultations/consultation_detail.html"
    context_object_name = "consultation"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("patient", "medecin", "constante", "ordonnance")
            .prefetch_related("ordonnance__lignes")
        )


class OrdonnanceUpdateView(MedecinMixin, UpdateView):
    model = Consultation
    fields = []
    template_name = "consultations/ordonnance_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.consultation = self.get_object()
        self.ordonnance, _ = Ordonnance.objects.get_or_create(consultation=self.consultation)
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(
            Consultation.objects.select_related("patient", "medecin"),
            pk=self.kwargs["pk"],
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["consultation"] = self.consultation
        ctx["patient"] = self.consultation.patient
        ctx["formset"] = kwargs.get("formset") or LigneOrdonnanceFormSet(instance=self.ordonnance)
        return ctx

    def post(self, request, *args, **kwargs):
        self.object = self.consultation
        formset = LigneOrdonnanceFormSet(request.POST, instance=self.ordonnance)
        if formset.is_valid():
            formset.save()
            messages.success(request, "Ordonnance enregistrée.")
            return redirect("consultations:detail", pk=self.consultation.pk)
        return self.render_to_response(self.get_context_data(formset=formset))


class OrdonnancePrintView(MedecinMixin, TemplateView):
    template_name = "consultations/ordonnance_print.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        consultation = get_object_or_404(
            Consultation.objects.select_related("patient", "medecin", "ordonnance"),
            pk=self.kwargs["pk"],
        )
        ordonnance, _ = Ordonnance.objects.get_or_create(consultation=consultation)
        ctx["consultation"] = consultation
        ctx["ordonnance"] = ordonnance
        ctx["patient"] = consultation.patient
        ctx["lignes"] = ordonnance.lignes.all()
        return ctx


class RendezVousListView(MedecinMixin, ListView):
    model = RendezVous
    template_name = "consultations/rdv_list.html"
    context_object_name = "rendez_vous"

    def get_queryset(self):
        return RendezVous.objects.select_related("patient", "medecin")


class RendezVousCreateView(MedecinMixin, CreateView):
    model = RendezVous
    form_class = RendezVousForm
    template_name = "consultations/rdv_form.html"
    success_url = reverse_lazy("consultations:rdv_liste")

    def get_patient_optional(self):
        pk = self.kwargs.get("patient_pk")
        if pk:
            return get_object_or_404(Patient, pk=pk)
        return None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["patient"] = self.get_patient_optional()
        return kwargs

    def form_valid(self, form):
        patient = self.get_patient_optional()
        if patient:
            form.instance.patient = patient
        form.instance.medecin = self.request.user
        messages.success(self.request, "Rendez-vous planifié.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["patient"] = self.get_patient_optional()
        return ctx


class RendezVousUpdateView(MedecinMixin, UpdateView):
    model = RendezVous
    form_class = RendezVousForm
    template_name = "consultations/rdv_form.html"
    success_url = reverse_lazy("consultations:rdv_liste")

    def form_valid(self, form):
        messages.success(self.request, "Rendez-vous mis à jour.")
        return super().form_valid(form)
