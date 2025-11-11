from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages

from tags.models import Etiqueta, PalabraEtiqueta
from groups.models import Grupo, UsuarioGrupo, GrupoPalabra
from dictionary.models import Palabra, Significado, Lectura, Nota
from progress.models import UsuarioPalabra

import core.utils as ut


def buscar_palabra(search_input, usuario):
    search_input_list = ut.set_alternate_inputs([search_input])
    owner_q = Q(usuario=usuario) | Q(usuario__perfil__rol="admin")
    exact_results = Palabra.objects.filter(
        owner_q,
        Q(palabra__in=search_input_list)
        | Q(significados__significado__in=search_input_list)
        | Q(lecturas__lectura__in=search_input_list)
        | Q(lecturas__lectura_limpia__in=search_input_list),
    ).distinct()
    related_queries = Q()
    for term in search_input_list:
        related_queries |= (
            Q(palabra__istartswith=term)
            | Q(significados__significado__istartswith=term)
            | Q(lecturas__lectura__istartswith=term)
            | Q(lecturas__lectura_limpia__istartswith=term)
        )
        startswith_results = (
            Palabra.objects.filter(owner_q, related_queries)
            .exclude(id__in=exact_results)
            .distinct()
        )
    related_queries = Q()
    for term in search_input_list:
        related_queries |= (
            Q(palabra__icontains=term)
            | Q(significados__significado__icontains=term)
            | Q(lecturas__lectura__icontains=term)
            | Q(lecturas__lectura_limpia__icontains=term)
        )
        contains_results = (
            Palabra.objects.filter(owner_q, related_queries)
            .exclude(id__in=exact_results)
            .exclude(id__in=startswith_results)
            .distinct()
        )

    return [list(exact_results), list(startswith_results) + list(contains_results)]


# __ Inputs
@login_required
def buscar_header(request, search_input, usuario):
    if not search_input:
        return redirect(request.META.get("HTTP_REFERER", "/"))
    ajustes = request.session.get("ajustes_buscar", {})
    ajustes.setdefault("buscando_tipo", "palabra")
    tipo = ajustes.get("buscando_tipo")
    exact_list = []
    related_list = []
    if tipo == "palabra":
        ajustes.setdefault("palabra_pasada", search_input)
        if ajustes.get("palabra_pasada") != search_input:
            ajustes["index_palabra"] = 0
            ajustes["palabra_pasada"] = search_input

        all_results = buscar_palabra(search_input, usuario)
        results = all_results[0] + all_results[1]
        exact_results = all_results[0]

        index = ajustes.get("index_palabra", 0)
        index = ut.bound_page_index(index, len(results))
        ajustes["index_palabra"] = index

        for i in range(index * 10, min(len(results), index * 10 + 10)):
            palabra = results[i]
            value = palabra.palabra_dict(usuario)
            if i < len(exact_results):
                exact_list.append(value)
            else:
                related_list.append(value)
            request.session["ajustes_buscar"] = ajustes
    elif tipo == "grupo":
        pass

    return (exact_list, related_list, index, len(results))


@require_POST
@login_required
def buscar_filtrar_grupo_actual(request, usuario):
    search_input = request.POST.get("buscar_palabra_agregar_a_grupo")
    grupo_id = request.session["grupo_actual"]
    exact_list, related_list = buscar_palabra(search_input, usuario)

    in_group_ids = set(
        GrupoPalabra.objects.filter(grupo_id=grupo_id).values_list(
            "palabra_id", flat=True
        )
    )

    exact_filtered = [p for p in exact_list if p.pk not in in_group_ids]
    related_filtered = [p for p in related_list if p.pk not in in_group_ids]

    return exact_filtered, related_filtered


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
    entry.toggle_estrella()
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
    # :: palabra_en_grupo :: las rows son grupos
    # :: grupo_tiene_palabra :: las rows son palabras
    elif (
        checkbox == "palabra_en_grupo" or checkbox == "grupo_tiene_palabra"
    ):  # rows de grupos
        if checkbox == "palabra_en_grupo":
            grupo_id = request.POST.get("check_id")
            palabra_id = request.session.get("palabra_actual")
        else:
            palabra_id = request.POST.get("check_id")
            grupo_id = request.session.get("grupo_actual")
        grupo_palabra = GrupoPalabra.objects.filter(
            grupo_id=grupo_id,
            palabra_id=palabra_id,
        )
        if grupo_palabra.exists():
            grupo_palabra.delete()
            messages.success(request, "Palabra eliminada de grupo exitosamente")
        else:
            GrupoPalabra.objects.create(
                grupo_id=grupo_id,
                palabra_id=palabra_id,
            )
            messages.success(request, "Palabra agregada a grupo exitosamente")
    elif checkbox == "etiqueta_en_palabra":
        etiqueta_id = request.POST.get("check_id")
        etiqueta_palabra = PalabraEtiqueta.objects.filter(id=etiqueta_id)
        if etiqueta_palabra.exists():
            etiqueta_palabra.delete()
            messages.success(request, "Etiqueta eliminada de palabra exitosamente")
        else:
            PalabraEtiqueta.objects.create(
                etiqueta_id=etiqueta_id, palabra_id=palabra_id, usuario=user
            )
            messages.success(request, "Etiqueta agregada a palabra exitosamente")
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
    elif switch == "filtros_palabras_exclusivo":
        ajustes["filtros_palabras_exclusivo"] = (
            False if ajustes.get("filtros_palabras_exclusivo", True) == True else True
        )
    elif switch == "filtros_etiquetas_andor":
        ajustes["filtros_etiquetas_andor"] = (
            "OR" if ajustes.get("filtros_etiquetas_andor", "AND") == "AND" else "AND"
        )
    elif switch == "filtros_etiquetas_exclusivo":
        ajustes["filtros_etiquetas_exclusivo"] = (
            False if ajustes.get("filtros_etiquetas_exclusivo", True) == True else True
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
