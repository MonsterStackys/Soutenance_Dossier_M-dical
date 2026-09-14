from django import forms

from .models import Patient


class BootstrapFormMixin:
    # Petite rustine : on met les classes Bootstrap sur tous les champs
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            extra = widget.attrs.get("class", "")
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs["class"] = f"{extra} form-check-input".strip()
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                widget.attrs["class"] = f"{extra} form-select".strip()
            elif isinstance(widget, forms.Textarea):
                widget.attrs["class"] = f"{extra} form-control".strip()
                widget.attrs.setdefault("rows", 3)
            else:
                widget.attrs["class"] = f"{extra} form-control".strip()


class PatientForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            "nom",
            "prenom",
            "date_naissance",
            "genre",
            "groupe_sanguin",
            "telephone",
            "adresse",
            "antecedent_medicaux",
            "antecedent_chirurgicaux",
            "allergies",
        ]
        widgets = {
            "date_naissance": forms.DateInput(attrs={"type": "date"}),
        }


class PatientSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        label="Recherche",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Nom, prénom ou numéro de dossier (PAT-2026-…)",
            }
        ),
    )
