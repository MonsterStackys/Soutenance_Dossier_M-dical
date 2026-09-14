from django.urls import path

from .views import (
    AuditListView,
    ProfilView,
    RoleLoginView,
    RoleLogoutView,
    UserCreateView,
    UserListView,
    UserUpdateView,
)

app_name = "accounts"  # pour écrire {% url 'accounts:login' %} dans les templates

urlpatterns = [
    path("connexion/", RoleLoginView.as_view(), name="login"),
    path("deconnexion/", RoleLogoutView.as_view(), name="logout"),
    path("profil/", ProfilView.as_view(), name="profil"),
    path("utilisateurs/", UserListView.as_view(), name="utilisateurs"),
    path("utilisateurs/nouveau/", UserCreateView.as_view(), name="utilisateur_creer"),
    path("utilisateurs/<int:pk>/modifier/", UserUpdateView.as_view(), name="utilisateur_modifier"),
    path("audit/", AuditListView.as_view(), name="audit"),
]
