from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Q
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, ListView, UpdateView

from .audit import enregistrer_audit
from .forms import ProfilPhotoForm, StyledAuthenticationForm, UserCreateForm, UserUpdateForm
from .models import AuditLog, User
from .permissions import AdminMixin


class RoleLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = StyledAuthenticationForm
    redirect_authenticated_user = True  # déjà connecté -> dashboard


class RoleLogoutView(LogoutView):
    next_page = reverse_lazy("accounts:login")

    def dispatch(self, request, *args, **kwargs):
        # On log avant le logout, sinon request.user devient anonyme
        if request.user.is_authenticated:
            enregistrer_audit(request, "DECONNEXION", "Déconnexion")
        return super().dispatch(request, *args, **kwargs)


class UserListView(AdminMixin, ListView):
    model = User
    template_name = "accounts/user_list.html"
    context_object_name = "utilisateurs"

    def get_queryset(self):
        return User.objects.all().order_by("role", "last_name")


class UserCreateView(AdminMixin, CreateView):
    model = User
    form_class = UserCreateForm
    template_name = "accounts/user_form.html"
    success_url = reverse_lazy("accounts:utilisateurs")

    def form_valid(self, form):
        messages.success(self.request, "Utilisateur créé.")
        return super().form_valid(form)


class UserUpdateView(AdminMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "accounts/user_form.html"
    success_url = reverse_lazy("accounts:utilisateurs")
    context_object_name = "agent"

    def form_valid(self, form):
        messages.success(self.request, "Fiche utilisateur mise à jour.")
        return super().form_valid(form)


class ProfilView(LoginRequiredMixin, UpdateView):
    # Chacun modifie sa propre fiche (photo, tel, nom)
    form_class = ProfilPhotoForm
    template_name = "accounts/profil.html"
    success_url = reverse_lazy("accounts:profil")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Profil mis à jour.")
        return super().form_valid(form)


class AuditListView(AdminMixin, ListView):
    # Par défaut : journal 24 h. ?archives=1 = les commandes déjà masquées.
    model = AuditLog
    template_name = "accounts/audit_list.html"
    context_object_name = "entrees"
    paginate_by = 30

    def get_queryset(self):
        qs = AuditLog.objects.select_related("utilisateur")
        archives = self.request.GET.get("archives") == "1"
        if archives:
            qs = qs.filter(efface_le__isnull=False)
        else:
            qs = qs.filter(efface_le__isnull=True)
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(utilisateur__username__icontains=q)
                | Q(utilisateur__last_name__icontains=q)
                | Q(action__icontains=q)
                | Q(description__icontains=q)
                | Q(chemin__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["archives"] = self.request.GET.get("archives") == "1"
        ctx["q"] = self.request.GET.get("q", "")
        ctx["maintenant"] = timezone.now()
        return ctx


from .audit import enregistrer_audit
from .forms import ProfilPhotoForm, StyledAuthenticationForm, UserCreateForm, UserUpdateForm
from .models import AuditLog, User
from .permissions import AdminMixin


class RoleLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = StyledAuthenticationForm
    redirect_authenticated_user = True


class RoleLogoutView(LogoutView):
    next_page = reverse_lazy("accounts:login")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            enregistrer_audit(request, "DECONNEXION", "Déconnexion")
        return super().dispatch(request, *args, **kwargs)


class UserListView(AdminMixin, ListView):
    model = User
    template_name = "accounts/user_list.html"
    context_object_name = "utilisateurs"

    def get_queryset(self):
        return User.objects.all().order_by("role", "last_name")


class UserCreateView(AdminMixin, CreateView):
    model = User
    form_class = UserCreateForm
    template_name = "accounts/user_form.html"
    success_url = reverse_lazy("accounts:utilisateurs")

    def form_valid(self, form):
        messages.success(self.request, "Utilisateur créé.")
        return super().form_valid(form)


class UserUpdateView(AdminMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "accounts/user_form.html"
    success_url = reverse_lazy("accounts:utilisateurs")
    context_object_name = "agent"

    def form_valid(self, form):
        messages.success(self.request, "Fiche utilisateur mise à jour.")
        return super().form_valid(form)


class ProfilView(LoginRequiredMixin, UpdateView):
    form_class = ProfilPhotoForm
    template_name = "accounts/profil.html"
    success_url = reverse_lazy("accounts:profil")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Profil mis à jour.")
        return super().form_valid(form)


class AuditListView(AdminMixin, ListView):
    """
    Journal quotidien (commandes des 24 h).
    ?archives=1 : commandes déjà effacées du journal, toujours en base.
    """

    model = AuditLog
    template_name = "accounts/audit_list.html"
    context_object_name = "entrees"
    paginate_by = 30

    def get_queryset(self):
        qs = AuditLog.objects.select_related("utilisateur")
        archives = self.request.GET.get("archives") == "1"
        if archives:
            qs = qs.filter(efface_le__isnull=False)
        else:
            qs = qs.filter(efface_le__isnull=True)
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(utilisateur__username__icontains=q)
                | Q(utilisateur__last_name__icontains=q)
                | Q(action__icontains=q)
                | Q(description__icontains=q)
                | Q(chemin__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["archives"] = self.request.GET.get("archives") == "1"
        ctx["q"] = self.request.GET.get("q", "")
        ctx["maintenant"] = timezone.now()
        return ctx
