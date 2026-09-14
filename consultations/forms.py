from typing import Optional

from django import forms
from django.forms import inlineformset_factory

from patients.forms import BootstrapFormMixin
from patients.models import Patient

from .models import Constante, Consultation, LigneOrdonnance, Ordonnance, RendezVous


class ConstanteForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Constante
        fields = [
            "tension_arterielle",
            "temperature",
            "poids",
            "taille",
            "frequence_cardiaque",
            "notes",
        ]
        widgets = {
            "tension_arterielle": forms.TextInput(attrs={"placeholder": "120/80"}),
        }


class ConsultationForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Consultation
        fields = ["constante", "motif", "symptomes", "diagnostic", "conduite_a_tenir"]
        widgets = {
            "symptomes": forms.Textarea(attrs={"rows": 3}),
            "diagnostic": forms.Textarea(attrs={"rows": 3}),
            "conduite_a_tenir": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, patient: Optional[Patient] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["constante"].required = False
        if patient is not None:
            # On ne propose que les constantes de CE patient
            self.fields["constante"].queryset = Constante.objects.filter(patient=patient)
            self.fields["constante"].empty_label = "Aucune constante liée"


class LigneOrdonnanceForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = LigneOrdonnance
        fields = ["medicament_nom", "posologie", "duree_traitement"]


LigneOrdonnanceFormSet = inlineformset_factory(
    Ordonnance,
    LigneOrdonnance,
    form=LigneOrdonnanceForm,
    extra=3,
    min_num=1,
    validate_min=True,
    can_delete=True,
)


class RendezVousForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = RendezVous
        fields = ["patient", "date_heure", "motif", "notes", "statut"]
        widgets = {
            "date_heure": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, patient: Optional[Patient] = None, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.date_heure:
            from django.utils import timezone as tz

            local = tz.localtime(self.instance.date_heure)
            self.initial["date_heure"] = local.strftime("%Y-%m-%dT%H:%M")
        if patient is not None:
            self.fields["patient"].initial = patient
            self.fields["patient"].widget = forms.HiddenInput()
            self.fields["patient"].queryset = Patient.objects.filter(pk=patient.pk)

