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
def toggle_modal(request):
    modal_settings = request.session.get("ajustes_modal", {})
    open_modal = modal_settings.get("open_modal", False)
    modal_settings["open_modal"] = not open_modal
    modal_settings["intentado"] = False
    request.session["ajustes_modal"] = modal_settings
    return redirect(request.META.get("HTTP_REFERER", "/"))


# bound ocurre dentro de llamada de context por si negativo
@require_POST
@login_required
def cambiar_pagina(request):
    action = request.POST.get("action")
    index = request.session.get("page_index", 0)
    if action == "next":
        index += 1
    elif action == "previous":
        index -= 1
    request.session["page_index"] = index
    return redirect(request.META.get("HTTP_REFERER", "/"))


def elegir_palabra(request):
    palabra_id = request.POST.get("wordcard")
    print(f"{palabra_id}: AAAAAAAAAAAAAAA")
    request.session["palabra_actual"] = palabra_id
    return redirect("detalles")


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
