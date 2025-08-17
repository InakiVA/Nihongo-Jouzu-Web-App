from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Q

from tags.models import Etiqueta, PalabraEtiqueta
from groups.models import Grupo, UsuarioGrupo, GrupoPalabra
from dictionary.models import Palabra, Significado, Lectura, Nota
from progress.models import UsuarioPalabra

import core.utils as ut


# __ Inputs
@login_required
def buscar(request, usuario):
    search_input = request.GET.get("search")
    search_input_list = ut.set_alternate_inputs([search_input])
    tipo = request.session.get("buscando_tipo", "palabra")
    if tipo == "palabra":
        results = Palabra.objects.filter(
            Q(usuario=usuario) | Q(usuario__perfil__rol="admin"),
            palabra__in=search_input_list,
        )
    elif tipo == "grupo":
        pass

    return results


# __ Swaps
@require_POST
@login_required
def toggle_estrella(request, objeto):
    swap_id = request.POST.get("swap_id")
    user = request.user
    if objeto == "grupo":
        entry = get_object_or_404(UsuarioGrupo, usuario=user, grupo_id=swap_id)
    elif objeto == "palabra":
        entry = get_object_or_404(UsuarioPalabra, usuario=user, palabra_id=swap_id)
    entry.estrella = not entry.estrella
    entry.save()
    return redirect(request.META.get("HTTP_REFERER", "/"))


@require_POST
@login_required
def toggle_filtro(request, view):
    filtro = request.POST.get("filter_id")
    if view == "inicio":
        ajustes = request.session.get("inicio_ajustes", {})

        if filtro in ajustes:
            ajustes[filtro] = not ajustes[filtro]
        else:
            ajustes[filtro] = True

        request.session["inicio_ajustes"] = ajustes
    return redirect(request.META.get("HTTP_REFERER", "/"))


# __ Checkboxes
@require_POST
@login_required
def toggle_checkbox(request, checkbox):
    if checkbox == "aleatorio":
        ajustes = request.session.get("inicio_ajustes", {})
        ajustes["aleatorio"] = not ajustes.get("aleatorio", False)
        request.session["inicio_ajustes"] = ajustes
    elif checkbox == "estudiando":
        grupo_id = request.POST.get("check_id")
        user = request.user
        entry = get_object_or_404(UsuarioGrupo, usuario=user, grupo_id=grupo_id)
        entry.estudiando = not entry.estudiando
        entry.save()
    elif checkbox == "palabra_en_grupo":
        grupo_id = request.POST.get("check_id")
        palabra_id = request.session.get("palabra_actual")
        grupo_palabra = GrupoPalabra.objects.filter(
            grupo_id=grupo_id,
            palabra_id=palabra_id,
        )
        if grupo_palabra.exists():
            grupo_palabra.delete()
        else:
            GrupoPalabra.objects.create(
                grupo_id=grupo_id,
                palabra_id=palabra_id,
            )
    return redirect(request.META.get("HTTP_REFERER", "/"))


# __ Switches
@require_POST
@login_required
def toggle_switch(request, switch):
    ajustes = request.session.get("inicio_ajustes", {})
    if switch == "descendente":
        ajustes["descendente"] = not ajustes.get("descendente", False)
    if switch == "filtros_palabras_andor":
        ajustes["filtros_palabras_andor"] = (
            "OR" if ajustes.get("filtros_palabras_andor", "AND") == "AND" else "AND"
        )
    elif switch == "filtros_palabras_inclusivo":
        ajustes["filtros_palabras_inclusivo"] = (
            False if ajustes.get("filtros_palabras_inclusivo", True) == True else True
        )
    elif switch == "filtros_etiquetas_andor":
        ajustes["filtros_etiquetas_andor"] = (
            "OR" if ajustes.get("filtros_etiquetas_andor", "AND") == "AND" else "AND"
        )
    elif switch == "filtros_etiquetas_inclusivo":
        ajustes["filtros_etiquetas_inclusivo"] = (
            False if ajustes.get("filtros_etiquetas_inclusivo", True) == True else True
        )
    request.session["inicio_ajustes"] = ajustes
    return redirect(request.META.get("HTTP_REFERER", "/"))


# __ Select
@require_POST
@login_required
def toggle_select(request, select):
    value = request.POST.get("select")
    if select == "orden_elegido":
        ajustes = request.session.get("inicio_ajustes", {})
        ajustes["orden_elegido"] = value
        request.session["inicio_ajustes"] = ajustes
    elif select == "idioma_preguntas_elegido":
        request.session["idioma_preguntas_elegido"] = value

    return redirect(request.META.get("HTTP_REFERER", "/"))
