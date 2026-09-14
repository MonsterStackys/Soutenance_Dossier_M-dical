# Mixins de droits. L'idée : chaque vue dit clairement qui a le droit.
# L'admin n'a PAS accès au clinique (patients, consultations, ordonnances).

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    allowed_roles = ()

    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        return user.role in self.allowed_roles

    def handle_no_permission(self):
        # Déjà connecté mais mauvais rôle -> 403 (pas un simple redirect login)
        if self.request.user.is_authenticated:
            raise PermissionDenied("Votre rôle ne permet pas d'accéder à cette page.")
        return super().handle_no_permission()


class AdminMixin(RoleRequiredMixin):
    allowed_roles = ("ADMIN",)


class ReceptionMixin(RoleRequiredMixin):
    allowed_roles = ("RECEPTIONNISTE",)


class InfirmierMixin(RoleRequiredMixin):
    allowed_roles = ("INFIRMIER",)


class MedecinMixin(RoleRequiredMixin):
    allowed_roles = ("MEDECIN",)


class SoignantMixin(RoleRequiredMixin):
    # consultations : les deux soignants
    allowed_roles = ("MEDECIN", "INFIRMIER")


class StaffDossierMixin(RoleRequiredMixin):
    # lecture des dossiers, sans l'admin
    allowed_roles = ("MEDECIN", "INFIRMIER", "RECEPTIONNISTE")
