# Dossier patient. Le n° PAT-AAAA-XXXX est généré tout seul à l'enregistrement.
from django.conf import settings
from django.db import models
from django.db.models import Max
from django.urls import reverse
from django.utils import timezone


class Patient(models.Model):
    class Genre(models.TextChoices):
        M = "M", "Masculin"
        F = "F", "Féminin"

    class GroupeSanguin(models.TextChoices):
        A_POS = "A+", "A+"
        A_NEG = "A-", "A-"
        B_POS = "B+", "B+"
        B_NEG = "B-", "B-"
        AB_POS = "AB+", "AB+"
        AB_NEG = "AB-", "AB-"
        O_POS = "O+", "O+"
        O_NEG = "O-", "O-"
        INCONNU = "INCONNU", "Inconnu"

    numero_dossier = models.CharField(
        "numéro de dossier",
        max_length=20,
        unique=True,
        editable=False,
        help_text="Généré automatiquement : PAT-AAAA-XXXX",
    )
    nom = models.CharField(max_length=80)
    prenom = models.CharField("prénom", max_length=80)
    date_naissance = models.DateField("date de naissance")
    genre = models.CharField(max_length=1, choices=Genre.choices)
    groupe_sanguin = models.CharField(
        max_length=8,
        choices=GroupeSanguin.choices,
        default=GroupeSanguin.INCONNU,
    )
    telephone = models.CharField("téléphone", max_length=30, blank=True)
    adresse = models.CharField(max_length=255, blank=True)
    antecedent_medicaux = models.TextField("antécédents médicaux", blank=True)
    antecedent_chirurgicaux = models.TextField("antécédents chirurgicaux", blank=True)
    allergies = models.TextField(blank=True)
    created_at = models.DateTimeField("créé le", auto_now_add=True)
    updated_at = models.DateTimeField("modifié le", auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="patients_crees",
        verbose_name="enregistré par",
    )

    class Meta:
        ordering = ["nom", "prenom"]
        verbose_name = "patient"
        verbose_name_plural = "patients"
        indexes = [
            models.Index(fields=["nom", "prenom"]),
            models.Index(fields=["numero_dossier"]),
        ]

    def __str__(self):
        return f"{self.numero_dossier} — {self.nom} {self.prenom}"

    def get_absolute_url(self):
        return reverse("patients:detail", kwargs={"pk": self.pk})

    def age(self):
        today = timezone.localdate()
        born = self.date_naissance
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

    def save(self, *args, **kwargs):
        if not self.numero_dossier:
            self.numero_dossier = self._generer_numero()
        super().save(*args, **kwargs)

    @classmethod
    def _generer_numero(cls):
        """PAT-2026-0001, séquence annuelle (évite les collisions via unique=True)."""
        annee = timezone.localdate().year
        prefixe = f"PAT-{annee}-"
        dernier = (
            cls.objects.filter(numero_dossier__startswith=prefixe)
            .aggregate(m=Max("numero_dossier"))
            .get("m")
        )
        if dernier:
            try:
                seq = int(dernier.split("-")[-1]) + 1
            except ValueError:
                seq = 1
        else:
            seq = 1
        return f"{prefixe}{seq:04d}"
