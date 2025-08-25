from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib import messages

import random
from core import utils as ut

from tags.models import Etiqueta
from groups.models import UsuarioGrupo, GrupoPalabra
from dictionary.models import Palabra
from progress.models import UsuarioPalabra


# __ Botones
@require_POST
@login_required
def preparar_estudio(request):
    request.session["index_palabra_pregunta"] = 0
    request.session["respuestas"] = []
    ajustes = request.session.get("inicio_ajustes", {})
    usuario = request.user

    palabras_obj_list = get_palabras_a_estudiar(usuario, ajustes)
    if not palabras_obj_list:
        messages.warning(
            request, "No hay palabras que estudiar con los filtros actuales"
        )
        return redirect("inicio")
    actualizar_grupos(usuario)
    palabras_id = [str(palabra.id) for palabra in palabras_obj_list]
    request.session["palabras_a_estudiar"] = palabras_id
    request.session["palabra_actual"] = palabras_id[0]
    contestadas = {}
    correctas = {}
    respuestas_incorrectas = {}
    for key in palabras_id:
        contestadas[key] = False
        correctas[key] = False
        respuestas_incorrectas[key] = []
    request.session["palabras_contestadas"] = contestadas
    request.session["palabras_correctas"] = correctas
    request.session["respuestas_incorrectas"] = respuestas_incorrectas
    return redirect("estudio")


@require_POST
@login_required
def checar_pregunta(request):
    user = request.user
    palabra_id = request.session.get("palabra_actual")
    palabra_obj = get_object_or_404(UsuarioPalabra, usuario=user, palabra_id=palabra_id)

    answer_input = request.POST.get("answer_input")

    if answer_input:
        respuestas = request.session.get("respuestas")

        is_correct = ut.check_answer(answer_input, respuestas)
        action = "plus" if is_correct else "minus"
        palabra_obj.progreso = ut.cambiar_progreso(palabra_obj.progreso, action)
        palabra_obj.save()

        palabras_contestadas = request.session.get("palabras_contestadas", {})
        palabras_correctas = request.session.get("palabras_correctas", {})

        palabras_contestadas[palabra_id] = True
        palabras_correctas[palabra_id] = is_correct

        request.session["palabras_contestadas"] = palabras_contestadas
        request.session["palabras_correctas"] = palabras_correctas

        if not is_correct:
            respuestas_incorrectas = request.session.get("respuestas_incorrectas", {})
            respuestas_incorrectas[palabra_id].append(answer_input)
            request.session["respuestas_incorrectas"] = respuestas_incorrectas

    return redirect(request.META.get("HTTP_REFERER", "/"))


# {} False si quedan por tener correctas, True si todas correctas
@require_POST
@login_required
def todas_contestadas_correctas(request):
    palabras_contestadas = request.session.get("palabras_contestadas", {})
    for palabra in palabras_contestadas:
        if not palabras_contestadas[palabra]:
            return False
    palabras_ids = []
    palabras_correctas = request.session.get("palabras_correctas", {})
    for palabra in palabras_correctas:
        if not palabras_correctas[palabra]:
            palabras_ids.append(palabra)
            palabras_contestadas[palabra] = False
    if not palabras_ids:
        return redirect("resultados")
    request.session["palabras_a_estudiar"] = palabras_ids
    request.session["index_palabra_pregunta"] = 0
    request.session["palabra_actual"] = palabras_ids[0]
    request.session["palabras_contestadas"] = palabras_contestadas
    return False


@require_POST
@login_required
def cambiar_pregunta(request):
    action = request.POST.get("action")
    if todas_contestadas_correctas(request):
        return redirect(reverse_lazy("resultados"))
    else:
        palabras_ids = request.session.get("palabras_a_estudiar", [])
        palabras_contestadas = request.session.get("palabras_contestadas")
        index = request.session.get("index_palabra_pregunta", 0)
        palabra_id = request.session.get("palabra_actual", palabras_ids[index])

        if action == "next" or action == "next_unanswered":
            original_id = palabra_id
            index = (index + 1) % len(palabras_ids)  # cíclico hacia adelante
            palabra_id = palabras_ids[index]
            if action == "next_unanswered":
                while palabras_contestadas[palabra_id] and palabra_id != original_id:
                    # skip a no contestada y al loopear, break
                    index = (index + 1) % len(palabras_ids)  # cíclico hacia adelante
                    palabra_id = palabras_ids[index]
        elif action == "previous" or action == "previous_unanswered":
            original_id = palabra_id
            index = (index - 1) % len(palabras_ids)  # cíclico hacia atrás
            palabra_id = palabras_ids[index]
            if action == "previous_unanswered":
                while palabras_contestadas[palabra_id] and palabra_id != original_id:
                    # skip a no contestada y al loopear, break
                    index = (index - 1) % len(palabras_ids)  # cíclico hacia atrás
                    palabra_id = palabras_ids[index]
        request.session["index_palabra_pregunta"] = index
        request.session["palabra_actual"] = palabra_id
        return redirect(request.META.get("HTTP_REFERER", "/"))


def actualizar_grupos(usuario):
    grupos_estudiando = UsuarioGrupo.objects.filter(usuario=usuario, estudiando=True)
    for grupo in grupos_estudiando:
        grupo.update_modificacion()
        grupo.save()


def get_palabras_a_estudiar(usuario, ajustes):
    # 1. Obtener palabras de grupos con estudiando=True
    grupos_estudiando_ids = UsuarioGrupo.objects.filter(
        usuario=usuario, estudiando=True
    ).values_list("grupo_id", flat=True)
    palabras_ids = (
        GrupoPalabra.objects.filter(grupo_id__in=grupos_estudiando_ids)
        .values_list("palabra_id", flat=True)
        .distinct()
    )

    palabras = Palabra.objects.filter(id__in=palabras_ids)

    # 2. Aplicar filtros de palabras
    condiciones = []
    filtros_palabras_exclusivo = ajustes.get("filtros_palabras_exclusivo", False)

    if ajustes.get("Creadas por mí (palabras)"):
        if not filtros_palabras_exclusivo:
            condiciones.append(Q(usuario=usuario))
        else:
            condiciones.append(~Q(usuario=usuario))

    if ajustes.get("Por completar (palabras)"):
        if not filtros_palabras_exclusivo:
            condiciones.append(
                Q(palabra_usuarios__usuario=usuario)
                & ~Q(palabra_usuarios__progreso=100)
            )
        else:
            condiciones.append(
                Q(palabra_usuarios__usuario=usuario) & Q(palabra_usuarios__progreso=100)
            )

    if ajustes.get("Con estrella (palabras)"):
        if not filtros_palabras_exclusivo:
            condiciones.append(
                Q(palabra_usuarios__usuario=usuario)
                & Q(palabra_usuarios__estrella=True)
            )
        else:
            condiciones.append(
                Q(palabra_usuarios__usuario=usuario)
                & Q(palabra_usuarios__estrella=False)
            )

    if condiciones:
        if ajustes.get("filtros_palabras_andor") == "OR":
            filtro_palabras = condiciones.pop()
            for cond in condiciones:
                filtro_palabras |= cond
        else:
            filtro_palabras = condiciones.pop()
            for cond in condiciones:
                filtro_palabras &= cond
        palabras = palabras.filter(filtro_palabras).distinct()

    # 3. Aplicar filtros de etiquetas
    etiquetas_activas = [
        key.replace(" (etiqueta)", "")
        for key, val in ajustes.items()
        if key.endswith(" (etiqueta)") and val is True
    ]

    if etiquetas_activas:
        etiquetas_obj = Etiqueta.objects.filter(etiqueta__in=etiquetas_activas)
        filtros_etiquetas_exclusivo = ajustes.get("filtros_etiquetas_exclusivo", True)
        filtros_etiquetas_or = ajustes.get("filtros_etiquetas_andor") == "OR"
        if not filtros_etiquetas_exclusivo:
            if filtros_etiquetas_or:
                palabras = palabras.filter(
                    palabra_etiquetas__etiqueta__in=etiquetas_obj
                ).distinct()
            else:
                for etiqueta in etiquetas_obj:
                    palabras = palabras.filter(palabra_etiquetas__etiqueta=etiqueta)
        else:
            if filtros_etiquetas_or:
                palabras = palabras.exclude(
                    palabra_etiquetas__etiqueta__in=etiquetas_obj
                ).distinct()
            else:
                for etiqueta in etiquetas_obj:
                    palabras = palabras.exclude(palabra_etiquetas__etiqueta=etiqueta)

    palabras = list(palabras)

    # 4. Aleatorizar si corresponde
    if ajustes.get("aleatorio"):
        random.shuffle(palabras)

    return palabras
