from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UsernameField

from patients.forms import BootstrapFormMixin

from .models import User


class StyledAuthenticationForm(AuthenticationForm):
    # On ajoute juste les classes Bootstrap, le reste est le login Django

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {"class": "form-control form-control-lg", "placeholder": "Identifiant", "autofocus": True}
        )
        self.fields["password"].widget.attrs.update(
            {"class": "form-control form-control-lg", "placeholder": "Mot de passe"}
        )


class UserCreateForm(BootstrapFormMixin, UserCreationForm):
    # Médecin / infirmier / réception — pas un 2e admin

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "telephone",
            "role",
            "photo",
            "password1",
            "password2",
        )
        field_classes = {"username": UsernameField}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["role"].choices = User.ROLES_CREABLES
        self.fields["photo"].required = False
        self.fields["photo"].widget.attrs["class"] = "form-control"


class UserUpdateForm(BootstrapFormMixin, forms.ModelForm):
    nouveau_mot_de_passe = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={"class": "form-control", "autocomplete": "new-password"}),
        help_text="Laisser vide pour ne pas changer le mot de passe.",
    )

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "telephone",
            "role",
            "photo",
            "is_active",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # On ne laisse pas changer le rôle d'un compte ADMIN depuis cet écran
        if self.instance and self.instance.role == User.Role.ADMIN:
            self.fields["role"].disabled = True
        else:
            self.fields["role"].choices = User.ROLES_CREABLES
        self.fields["photo"].required = False
        self.fields["photo"].widget.attrs["class"] = "form-control"

    def save(self, commit=True):
        user = super().save(commit=False)
        pwd = self.cleaned_data.get("nouveau_mot_de_passe")
        if pwd:
            user.set_password(pwd)
        if commit:
            user.save()
        return user


class ProfilPhotoForm(BootstrapFormMixin, forms.ModelForm):
    # Photo + infos perso de la personne connectée

    class Meta:
        model = User
        fields = ("photo", "telephone", "first_name", "last_name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["photo"].widget.attrs["class"] = "form-control"
