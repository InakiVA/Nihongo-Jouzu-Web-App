from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages

from dictionary.models import Palabra, Significado, Lectura, Nota
from progress.models import UsuarioPalabra
from groups.models import Grupo, UsuarioGrupo


@require_POST
@login_required
def crear_grupo(request):
    ajustes = request.session.get("ajustes_grupos", {})
    grupo_value = request.POST.get("grupo_nuevo")
    desc_value = request.POST.get("descripcion_nueva")
    user = request.user
    existent = Grupo.objects.filter(
        Q(usuario=user) | Q(usuario__perfil__rol="admin"), grupo=grupo_value
    ).exists()
    breaker = False
    if "<" in grupo_value or ">" in grupo_value:
        breaker = True
        messages.warning(request, "Grupo no puede contener '<' o '>'")
    if "<" in desc_value or ">" in desc_value:
        breaker = True
        messages.warning(request, "Descripción no puede contener '<' o '>'")
    if not grupo_value or existent or breaker:
        for key, value in zip(
            ["grupo_valido", "desc_valida"],
            [grupo_value, desc_value],
        ):
            ajustes[key] = value
        request.session["ajustes_grupos"] = ajustes
        if not grupo_value:
            messages.error(request, "Favor de ingresar nombre de grupo")
        if existent:
            messages.error(request, "Ya existe un grupo con este nombre")
        return redirect(request.META.get("HTTP_REFERER", "/"))
    for key, value in zip(
        ["grupo_valido", "desc_valida"],
        ["", ""],
    ):
        ajustes[key] = value

    grupo_obj = Grupo.objects.create(
        usuario=user, grupo=grupo_value, descripcion=desc_value
    )
    UsuarioGrupo.objects.create(usuario=user, grupo=grupo_obj)

    request.session["grupo_actual"] = grupo_obj.id
    request.session["ajustes_grupos"] = ajustes
    messages.success(request, "Grupo creado exitosamente")
    return redirect("detalles_grupo")


@require_POST
@login_required
def editar_grupo_atributos(request, atributo):
    grupo_id = request.session.get("grupo_actual", None)
    grupo_obj = get_object_or_404(Grupo, id=grupo_id)
    user = request.user
    if not grupo_obj or grupo_obj.usuario != user:
        return redirect(request.META.get("HTTP_REFERER", "/"))
    if atributo == "grupo":
        value = request.POST.get("update_grupo")
        if not value:
            messages.warning(
                request, "No se ingresó el nombre de grupo para actualizar"
            )
            return redirect(request.META.get("HTTP_REFERER", "/"))
        existent = Grupo.objects.filter(usuario=user, grupo=value).exists()
        if existent:
            if value == grupo_obj.grupo:
                messages.info(request, "El nombre del grupo es el mismo")
            else:
                messages.warning(request, "Ya creaste un grupo con este nombre")
            return redirect(request.META.get("HTTP_REFERER", "/"))
        if "<" in value or ">" in value:
            messages.warning(request, "Grupo no puede contener '<' o '>'")
            return redirect(request.META.get("HTTP_REFERER", "/"))
        grupo_obj.update_grupo(value)
        messages.success(request, "Nombre del grupo actualizado exitosamente")
    elif atributo == "descripcion":
        value = request.POST.get("update_descripcion")
        if not value:
            messages.warning(
                request,
                "No se ingresó la descripción de grupo para actualizar",
            )
            return redirect(request.META.get("HTTP_REFERER", "/"))
        if value == grupo_obj.descripcion:
            messages.info(request, "La descripción del grupo es la misma")
            return redirect(request.META.get("HTTP_REFERER", "/"))
        if "<" in value or ">" in value:
            messages.warning(request, "Descripción no puede contener '<' o '>'")
            return redirect(request.META.get("HTTP_REFERER", "/"))
        grupo_obj.update_descripcion(value)
        messages.success(request, "Descripción del grupo actualizado exitosamente")
    return redirect(request.META.get("HTTP_REFERER", "/"))


@require_POST
@login_required
def eliminar_grupo(request):
    grupo_id = request.session.get("grupo_actual", None)
    grupo_obj = get_object_or_404(Grupo, id=grupo_id)
    user = request.user
    if not grupo_obj or grupo_obj.usuario != user:
        return redirect(request.META.get("HTTP_REFERER", "/"))
    grupo_obj.delete()
    messages.success(request, "Grupo eliminado exitosamente")
    return redirect("grupos")
