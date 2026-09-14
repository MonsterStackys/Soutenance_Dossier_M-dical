# Compte du personnel : on part d'AbstractUser et on ajoute le rôle + la photo.
from django.contrib.auth.models import AbstractUser
from django.db import models


def photo_upload_to(instance, filename):
    # On garde l'extension d'origine, le nom du fichier = identifiant
    if "." in filename:
        ext = filename.rsplit(".", 1)[-1].lower()
    else:
        ext = "jpg"
    identifiant = instance.username or "user"
    return f"photos/{identifiant}.{ext}"


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrateur"
        MEDECIN = "MEDECIN", "Médecin"
        INFIRMIER = "INFIRMIER", "Infirmier"
        RECEPTIONNISTE = "RECEPTIONNISTE", "Réceptionniste"

    # L'admin ne crée pas un autre admin depuis l'écran métier
    ROLES_CREABLES = (
        (Role.MEDECIN, "Médecin"),
        (Role.INFIRMIER, "Infirmier"),
        (Role.RECEPTIONNISTE, "Réceptionniste"),
    )

    role = models.CharField(
        "rôle",
        max_length=20,
        choices=Role.choices,
        default=Role.RECEPTIONNISTE,
        help_text="Ça décide ce que la personne a le droit de faire.",
    )
    telephone = models.CharField("téléphone", max_length=30, blank=True)
    photo = models.ImageField(
        "photo de profil",
        upload_to=photo_upload_to,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "utilisateur"
        verbose_name_plural = "utilisateurs"
        ordering = ["last_name", "first_name", "username"]

    def __str__(self):
        nom = self.get_full_name().strip() or self.username
        return f"{nom} ({self.get_role_display()})"

    def is_admin(self):
        return self.role == self.Role.ADMIN

    def is_medecin(self):
        return self.role == self.Role.MEDECIN

    def is_infirmier(self):
        return self.role == self.Role.INFIRMIER

    def is_receptionniste(self):
        return self.role == self.Role.RECEPTIONNISTE

    def is_soignant(self):
        # médecin ou infirmier — pas l'admin, pas la réception
        return self.role in (self.Role.MEDECIN, self.Role.INFIRMIER)


class AuditLog(models.Model):
    # Une ligne = une commande (souvent un POST).
    # Au bout de 24 h on la masque (efface_le) mais on ne la delete pas.

    utilisateur = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audits",
    )
    action = models.CharField(max_length=80)
    description = models.TextField(blank=True)
    methode = models.CharField(max_length=10, blank=True)
    chemin = models.CharField(max_length=255, blank=True)
    adresse_ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField("enregistré le", auto_now_add=True)
    efface_le = models.DateTimeField("effacé du journal le", null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "entrée d'audit"
        verbose_name_plural = "journal d'audit"

    def __str__(self):
        qui = self.utilisateur.username if self.utilisateur else "anonyme"
        return f"{self.created_at:%d/%m %H:%M} — {qui} — {self.action}"

    @property
    def est_efface(self):
        return self.efface_le is not None
