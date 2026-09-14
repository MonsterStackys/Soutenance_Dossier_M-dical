def role_flags(request):
    # Pour le menu : savoir qui est qui sans tout recalculer dans chaque template
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {
            "is_admin_role": False,
            "is_medecin_role": False,
            "is_infirmier_role": False,
            "is_reception_role": False,
            "is_soignant_role": False,
        }
    return {
        "is_admin_role": user.is_admin(),
        "is_medecin_role": user.is_medecin(),
        "is_infirmier_role": user.is_infirmier(),
        "is_reception_role": user.is_receptionniste(),
        "is_soignant_role": user.is_soignant(),
    }


def structure(_request):
    from django.conf import settings

    return {"NOM_STRUCTURE": getattr(settings, "NOM_STRUCTURE", "Poste de Santé Khar Yalla")}
