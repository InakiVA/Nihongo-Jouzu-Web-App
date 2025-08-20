from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.db.models import Q

from tags.models import Etiqueta, PalabraEtiqueta, GrupoEtiqueta
from groups.models import Grupo, UsuarioGrupo, GrupoPalabra
from dictionary.models import Palabra, Significado, Lectura, Nota
from progress.models import UsuarioPalabra

import core.utils as ut


def elegir_palabra(request):
    palabra_id = request.POST.get("wordcard")
    request.session["palabra_actual"] = palabra_id
    return redirect("detalles")


@require_POST
@login_required
def toggle_modal(request):
    print(dict(request.session))
    modal_settings = request.session.get("ajustes_palabras", {})
    open_modal = modal_settings.get("open_modal", False)
    modal_settings["open_modal"] = not open_modal
    modal_settings["intentado"] = False
    request.session["ajustes_palabras"] = modal_settings
    return redirect(request.META.get("HTTP_REFERER", "/"))


# ** bound ocurre dentro de llamada de context por si negativo
@require_POST
@login_required
def cambiar_pagina(request, pagina):
    action = request.POST.get("action")
    if action == "next":
        change = 1
    elif action == "previous":
        change = -1
    if pagina == "palabras":
        ajustes_palabras = request.session.get("ajustes_palabras", {})
        index = ajustes_palabras.get("page_index", 0)
        index += change
        ajustes_palabras["page_index"] = index
        request.session["ajustes_palabras"] = ajustes_palabras

    return redirect(request.META.get("HTTP_REFERER", "/"))


@require_POST
@login_required
# () tipo ["Significado","Lectura","Nota","Etiqueta"]
def agregar_a_palabra(request, tipo):
    user = request.user
    palabra_id = int(request.session.get("palabra_actual"))
    palabra_obj = get_object_or_404(Palabra, id=palabra_id)

    if tipo == "Significado":
        input_value = request.POST.get("agregar_significado")
        if input_value:
            Significado.objects.create(
                significado=input_value, palabra=palabra_obj, usuario=user
            )
    elif tipo == "Lectura":
        input_value = request.POST.get("agregar_lectura")
        if input_value:
            Lectura.objects.create(
                lectura=input_value, palabra=palabra_obj, usuario=user
            )
    elif tipo == "Nota":
        input_value = request.POST.get("agregar_nota")
        if input_value:
            Nota.objects.create(nota=input_value, palabra=palabra_obj, usuario=user)
    elif tipo == "Etiqueta":
        input_value = request.POST.get("agregar_etiqueta")
        etiquetas_dict = request.session.get("new_etiquetas", {})
        etiqueta_id = etiquetas_dict[input_value]
        PalabraEtiqueta.objects.create(
            etiqueta_id=etiqueta_id, palabra=palabra_obj, usuario=user
        )

    return redirect(request.META.get("HTTP_REFERER", "/"))


@require_POST
@login_required
def cambiar_progreso(request):
    user = request.user
    action = request.POST.get("action")
    palabra_id = request.session.get("palabra_actual")
    palabra_obj = get_object_or_404(UsuarioPalabra, usuario=user, palabra_id=palabra_id)
    progreso = palabra_obj.progreso

    if action == "slider":
        try:
            progreso = int(request.POST.get("slider_value", progreso))
        except ValueError:
            pass
    else:  # plus, minus
        progreso = ut.cambiar_progreso(progreso, action)

    palabra_obj.progreso = progreso
    palabra_obj.save()

    return redirect(request.META.get("HTTP_REFERER", "/"))


@login_required
def asegurar_ajustes_sesion(request):
    ajustes_default = {
        "orden_elegido": "Creación",
        "descendente": False,
        "idioma_preguntas": "Original",
        "aleatorio": False,
        "filtros_palabras_andor": "AND",
        "filtros_palabras_exclusivo": True,
        "filtros_etiquetas_andor": "AND",
        "filtros_etiquetas_exclusivo": True,
    }
    if "inicio_ajustes" not in request.session:
        request.session["inicio_ajustes"] = ajustes_default.copy()
    else:
        for key, val in ajustes_default.items():
            request.session["inicio_ajustes"].setdefault(key, val)


def crear_palabras_nuevas_del_admin(usuario):
    ids_objetivo = set(
        Palabra.objects.filter(
            Q(usuario=usuario) | Q(usuario__perfil__rol="admin")
        ).values_list("id", flat=True)
    )  # que registro sea de admin o de usuario
    ids_existentes = set(
        UsuarioPalabra.objects.filter(usuario=usuario).values_list(
            "palabra_id", flat=True
        )
    )  # registros ya en tabla relacional
    ids_nuevos = ids_objetivo - ids_existentes

    if ids_nuevos:
        palabras_nuevas = Palabra.objects.filter(id__in=ids_nuevos).order_by("id")
        for palabra in palabras_nuevas:
            UsuarioPalabra.objects.create(
                usuario=usuario,
                palabra=palabra,
                progreso=0,
                estrella=False,
            )


def crear_grupos_nuevos_del_admin(usuario):
    ids_objetivo = set(
        Grupo.objects.filter(
            Q(usuario=usuario) | Q(usuario__perfil__rol="admin")
        ).values_list("id", flat=True)
    )  # que registro sea de admin o de usuario
    ids_existentes = set(
        UsuarioGrupo.objects.filter(usuario=usuario).values_list("grupo_id", flat=True)
    )  # registros ya en tabla relacional
    ids_nuevos = ids_objetivo - ids_existentes

    if ids_nuevos:
        grupos_nuevos = Grupo.objects.filter(id__in=ids_nuevos).order_by("id")
        for grupo in grupos_nuevos:
            UsuarioGrupo.objects.create(
                usuario=usuario,
                grupo=grupo,
                estudiando=False,
                estrella=False,
            )


def get_user_groups_list(usuario):
    usuario_palabras = UsuarioPalabra.objects.filter(usuario=usuario)
    progreso_map = {up.palabra_id: up.progreso for up in usuario_palabras}

    usuario_grupos = (
        UsuarioGrupo.objects.filter(usuario=usuario)
        .select_related("grupo")  # para acceder a ug.grupo sin query extra
        .prefetch_related("grupo__grupo_palabras")  # para las palabras en el grupo
        .order_by("id")
    )

    grupos = []
    for ug in usuario_grupos:
        palabras = [gp.palabra_id for gp in ug.grupo.grupo_palabras.all()]
        progreso_total = sum(progreso_map.get(pid, 0) for pid in palabras)
        cantidad = len(palabras)
        progreso = int(progreso_total / cantidad) if cantidad > 0 else 0

        grupos.append(
            {
                "text": ug.grupo.grupo,
                "id": ug.grupo.id,
                "progreso": progreso,
                "estrella": ug.estrella,
                "estudiando": ug.estudiando,
                "fecha_creacion": ug.grupo.fecha_creacion,
                "ultima_modificacion": ug.ultima_modificacion,
                "autor": ug.grupo.usuario.username,
            }
        )
    return grupos
