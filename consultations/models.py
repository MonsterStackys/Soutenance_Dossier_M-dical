# Constantes, consultation, ordonnance, RDV.
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Constante(models.Model):
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="constantes",
    )
    date = models.DateTimeField(default=timezone.now)
    tension_arterielle = models.CharField(
        "tension artérielle",
        max_length=15,
        help_text="Ex. 120/80",
    )
    temperature = models.DecimalField("température (°C)", max_digits=4, decimal_places=1)
    poids = models.DecimalField("poids (kg)", max_digits=5, decimal_places=1)
    taille = models.DecimalField("taille (cm)", max_digits=5, decimal_places=1)
    frequence_cardiaque = models.PositiveSmallIntegerField("fréquence cardiaque (bpm)")
    pris_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="constantes_prises",
        verbose_name="pris par",
    )
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-date"]
        verbose_name = "constante"
        verbose_name_plural = "constantes"

    def __str__(self):
        return f"Constantes {self.patient} — {self.date:%d/%m/%Y %H:%M}"

    def imc(self):
        if not self.taille:
            return None
        metres = float(self.taille) / 100
        if metres <= 0:
            return None
        return round(float(self.poids) / (metres * metres), 1)


class Consultation(models.Model):
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="consultations",
    )
    medecin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="consultations_medecin",
        verbose_name="réalisé par",
    )
    constante = models.ForeignKey(
        Constante,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="consultations",
    )
    motif = models.CharField(max_length=255)
    symptomes = models.TextField("symptômes", blank=True)
    diagnostic = models.TextField()
    conduite_a_tenir = models.TextField("conduite à tenir", blank=True)
    date_consultation = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-date_consultation"]
        verbose_name = "consultation"
        verbose_name_plural = "consultations"

    def __str__(self):
        return f"Consultation {self.patient} — {self.date_consultation:%d/%m/%Y}"

    def get_absolute_url(self):
        return reverse("consultations:detail", kwargs={"pk": self.pk})


class Ordonnance(models.Model):
    consultation = models.OneToOneField(
        Consultation,
        on_delete=models.CASCADE,
        related_name="ordonnance",
    )
    date_creation = models.DateTimeField(default=timezone.now)
    mention = models.CharField(
        max_length=255,
        blank=True,
        default="À renouveler uniquement sur avis médical.",
    )

    class Meta:
        verbose_name = "ordonnance"
        verbose_name_plural = "ordonnances"

    def __str__(self):
        return f"Ordonnance #{self.pk} — {self.consultation.patient}"

    def get_print_url(self):
        return reverse("consultations:ordonnance_imprimer", kwargs={"pk": self.consultation_id})


class RendezVous(models.Model):
    class Statut(models.TextChoices):
        PLANIFIE = "PLANIFIE", "Planifié"
        HONORE = "HONORE", "Honoré"
        ANNULE = "ANNULE", "Annulé"

    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="rendez_vous",
    )
    medecin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="rendez_vous_medecin",
        verbose_name="médecin",
    )
    date_heure = models.DateTimeField("date et heure")
    motif = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    statut = models.CharField(max_length=12, choices=Statut.choices, default=Statut.PLANIFIE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date_heure"]
        verbose_name = "rendez-vous"
        verbose_name_plural = "rendez-vous"

    def __str__(self):
        return f"RDV {self.patient} — {self.date_heure:%d/%m/%Y %H:%M}"

    def get_absolute_url(self):
        return reverse("consultations:rdv_liste")


class LigneOrdonnance(models.Model):
    ordonnance = models.ForeignKey(
        Ordonnance,
        on_delete=models.CASCADE,
        related_name="lignes",
    )
    medicament_nom = models.CharField("médicament", max_length=120)
    posologie = models.CharField(max_length=120)
    duree_traitement = models.CharField("durée du traitement", max_length=80)

    class Meta:
        verbose_name = "ligne d'ordonnance"
        verbose_name_plural = "lignes d'ordonnance"

    def __str__(self):
        return f"{self.medicament_nom} — {self.posologie}"
