from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, get_object_or_404

from dictionary.models import Palabra, Significado, Lectura
from progress.models import UsuarioPalabra
from groups.models import Grupo


@require_POST
@login_required
def crear_palabra(request):
    modal_settings = request.session.get("ajustes_modal")
    modal_settings["intentado"] = True
    palabra_value = request.POST.get("palabra_nueva")
    significado_value = request.POST.get("significado_nuevo")
    lectura_value = request.POST.get("lectura_nueva")
    if False == all([palabra_value, significado_value, lectura_value]):
        for key, value in zip(
            ["palabra_valida", "significado_valido", "lectura_valida"],
            [palabra_value, significado_value, lectura_value],
        ):
            modal_settings[key] = value
        request.session["ajustes_modal"] = modal_settings
        return redirect(request.META.get("HTTP_REFERER", "/"))
    for key, value in zip(
        ["palabra_valida", "significado_valido", "lectura_valida"],
        ["", "", ""],
    ):
        modal_settings[key] = value
    modal_settings["open_modal"] = not modal_settings["open_modal"]
    user = request.user
    palabra_obj = Palabra.objects.create(usuario=user, palabra=palabra_value)
    UsuarioPalabra.objects.create(usuario=user, palabra=palabra_obj)
    Significado.objects.create(
        significado=significado_value, palabra=palabra_obj, usuario=user
    )
    Lectura.objects.create(lectura=lectura_value, palabra=palabra_obj, usuario=user)
    request.session["palabra_actual"] = palabra_obj.id
    request.session["ajustes_modal"] = modal_settings
    return redirect("detalles")
