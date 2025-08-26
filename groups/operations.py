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
    existent = Grupo.objects.filter(usuario=user, grupo=grupo_value).exists()
    if not grupo_value or existent:
        for key, value in zip(
            ["grupo_valido", "desc_valida"],
            [grupo_value, desc_value],
        ):
            ajustes[key] = value
        request.session["ajustes_grupos"] = ajustes
        if not grupo_value:
            messages.error(request, "Favor de ingresar nombre de grupo")
        if existent:
            messages.error(request, "Ya creaste un grupo con este nombre")
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
