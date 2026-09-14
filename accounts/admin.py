from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import AuditLog, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("username", "last_name", "first_name", "role", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_staff")
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Poste de Santé Khar Yalla", {"fields": ("role", "telephone", "photo")}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ("Poste de Santé Khar Yalla", {"fields": ("role", "telephone", "first_name", "last_name", "photo")}),
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "utilisateur", "action", "chemin", "efface_le")
    list_filter = ("action",)
    search_fields = ("utilisateur__username", "action", "description", "chemin")
    readonly_fields = (
        "utilisateur",
        "action",
        "description",
        "methode",
        "chemin",
        "adresse_ip",
        "created_at",
        "efface_le",
    )
