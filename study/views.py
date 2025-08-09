from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.shortcuts import redirect, get_object_or_404
import random

from tags.models import Etiqueta, PalabraEtiqueta
from groups.models import Grupo, UsuarioGrupo, GrupoPalabra
from dictionary.models import Palabra, Significado, Lectura, Nota
from progress.models import UsuarioPalabra

from core import utils as ut


# __ Checkboxes
@require_POST
@login_required
def toggle_aleatorio(request):
    ajustes = request.session.get("inicio_ajustes", {})
    ajustes["aleatorio"] = not ajustes.get("aleatorio", False)
    request.session["inicio_ajustes"] = ajustes
    return redirect(request.META.get("HTTP_REFERER", "/"))


@require_POST
@login_required
def toggle_estudiando(request):
    grupo_id = request.POST.get("check_id")
    user = request.user
    entry = get_object_or_404(UsuarioGrupo, usuario=user, grupo_id=grupo_id)
    entry.estudiando = not entry.estudiando
    entry.save()
    return redirect(request.META.get("HTTP_REFERER", "/"))


# __ Switches
@require_POST
@login_required
def toggle_descendente(request):
    ajustes = request.session.get("inicio_ajustes", {})
    ajustes["descendente"] = not ajustes.get("descendente", False)
    request.session["inicio_ajustes"] = ajustes
    return redirect(request.META.get("HTTP_REFERER", "/"))


@require_POST
@login_required
def toggle_filtros_palabras(request):
    ajustes = request.session.get("inicio_ajustes", {})
    ajustes["filtros_palabras"] = (
        "OR" if ajustes.get("filtros_palabras", "AND") == "AND" else "AND"
    )
    request.session["inicio_ajustes"] = ajustes
    return redirect(request.META.get("HTTP_REFERER", "/"))


@require_POST
@login_required
def toggle_filtros_etiquetas_switch(request):
    ajustes = request.session.get("inicio_ajustes", {})
    ajustes["filtros_etiquetas"] = (
        "OR" if ajustes.get("filtros_etiquetas", "AND") == "AND" else "AND"
    )
    request.session["inicio_ajustes"] = ajustes
    return redirect(request.META.get("HTTP_REFERER", "/"))


# __ Swaps
@require_POST
@login_required
def toggle_estrella_grupo(request):
    grupo_id = request.POST.get("swap_id")
    user = request.user
    entry = get_object_or_404(UsuarioGrupo, usuario=user, grupo_id=grupo_id)
    entry.estrella = not entry.estrella
    entry.save()
    return redirect(request.META.get("HTTP_REFERER", "/"))


@require_POST
@login_required
def toggle_estrella_palabra(request):
    palabra_id = request.POST.get("swap_id")
    user = request.user
    entry = get_object_or_404(UsuarioPalabra, usuario=user, palabra_id=palabra_id)
    entry.estrella = not entry.estrella
    entry.save()
    return redirect(request.META.get("HTTP_REFERER", "/"))


@require_POST
@login_required
def toggle_filtro(request):
    filtro = request.POST.get("filter_id")
    ajustes = request.session.get("inicio_ajustes", {})

    if filtro in ajustes:
        ajustes[filtro] = not ajustes[filtro]
    else:
        ajustes[filtro] = True

    request.session["inicio_ajustes"] = ajustes
    return redirect(request.META.get("HTTP_REFERER", "/"))


# __ Selects
@require_POST
@login_required
def toggle_orden_select(request):
    ajustes = request.session.get("inicio_ajustes", {})
    value = request.POST.get("select")
    if value:
        ajustes["orden_elegido"] = value
        request.session["inicio_ajustes"] = ajustes
    return redirect(request.META.get("HTTP_REFERER", "/"))


@require_POST
@login_required
def toggle_idioma_preguntas(request):
    value = request.POST.get("select")
    if value:
        request.session["idioma_preguntas_elegido"] = value
    return redirect(request.META.get("HTTP_REFERER", "/"))


# __ Botones
@require_POST
@login_required
def preparar_estudio(request):
    request.session["index_palabra_pregunta"] = 0
    request.session["respuestas"] = []
    ajustes = request.session.get("inicio_ajustes", {})
    usuario = request.user

    actualizar_grupos(usuario)

    palabras_qs = get_palabras_a_estudiar(usuario, ajustes)
    if not palabras_qs:
        messages.warning(
            request, "No hay palabras que estudiar con los filtros actuales."
        )
        return redirect(request.META.get("HTTP_REFERER", "/"))
    palabras_id = [str(palabra.id) for palabra in palabras_qs]
    request.session["palabras_a_estudiar"] = palabras_id
    request.session["palabra_actual"] = palabras_id[0]
    contestadas = {}
    correctas = {}
    for key in palabras_id:
        contestadas[key] = False
        correctas[key] = False
    request.session["palabras_contestadas"] = contestadas
    request.session["palabras_correctas"] = correctas
    return redirect("estudio")


@require_POST
@login_required
# () tipo ["Significado","Lectura","Nota","Etiqueta"]
def agregar_a_palabra(request, tipo):
    print("ALL POST DATA:", request.POST.dict())

    user = request.user
    palabra_id = int(request.session.get("palabra_actual"))
    palabra_obj = get_object_or_404(Palabra, id=palabra_id)

    if tipo == "Significado":
        input_value = request.POST.get("agregar_significado")
        Significado.objects.create(
            significado=input_value, palabra=palabra_obj, usuario=user
        )
    elif tipo == "Lectura":
        input_value = request.POST.get("agregar_lectura")
        Lectura.objects.create(lectura=input_value, palabra=palabra_obj, usuario=user)
    elif tipo == "Nota":
        input_value = request.POST.get("agregar_nota")
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

    return redirect(request.META.get("HTTP_REFERER", "/"))


@require_POST
@login_required
def cambiar_pregunta(request):
    action = request.POST.get("action")
    palabras_ids = request.session.get("palabras_a_estudiar", [])
    palabras_contestadas = request.session.get("palabras_contestadas")
    index = request.session.get("index_palabra_pregunta", 0)
    palabra_id = request.session.get("palabra_actual", palabras_ids[index])

    if action == "next" or action == "next_unanswered":
        index = (index + 1) % len(palabras_ids)  # cíclico hacia adelante
        palabra_id = palabras_ids[index]
        original_id = palabra_id
        if action == "next_unanswered":
            while palabras_contestadas[palabra_id] and palabra_id != original_id:
                # skip a no contestada y al loopear, break
                index = (index + 1) % len(palabras_ids)  # cíclico hacia adelante
                palabra_id = palabras_ids[index]
    elif action == "previous" or action == "previous_unanswered":
        index = (index - 1) % len(palabras_ids)  # cíclico hacia atrás
        palabra_id = palabras_ids[index]
        original_id = palabra_id
        if action == "previous_unanswered":
            while palabras_contestadas[palabra_id] and palabra_id != original_id:
                # skip a no contestada y al loopear, break
                index = (index - 1) % len(palabras_ids)  # cíclico hacia atrás
                palabra_id = palabras_ids[index]

    request.session["index_palabra_pregunta"] = index
    request.session["palabra_actual"] = palabra_id
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

    if ajustes.get("Creadas por mí (palabras)"):
        condiciones.append(Q(usuario=usuario))

    if ajustes.get("Por completar (palabras)"):
        condiciones.append(
            Q(palabra_usuarios__usuario=usuario) & ~Q(palabra_usuarios__progreso=100)
        )

    if ajustes.get("Con estrella (palabras)"):
        condiciones.append(
            Q(palabra_usuarios__usuario=usuario) & Q(palabra_usuarios__estrella=True)
        )

    if condiciones:
        if ajustes.get("filtros_palabras") == "OR":
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
        if ajustes.get("filtros_etiquetas") == "OR":
            palabras = palabras.filter(
                palabra_etiquetas__etiqueta__in=etiquetas_obj
            ).distinct()
        else:
            for etiqueta in etiquetas_obj:
                palabras = palabras.filter(palabra_etiquetas__etiqueta=etiqueta)

    palabras = list(palabras)

    # 4. Aleatorizar si corresponde
    if ajustes.get("aleatorio"):
        random.shuffle(palabras)

    return palabras


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "study/home.html"

    def asegurar_ajustes_sesion(self):
        ajustes_default = {
            "orden_elegido": "Creación",
            "descendente": False,
            "idioma_preguntas": "Original",
            "aleatorio": False,
            "filtros_palabras": "AND",
            "filtros_etiquetas": "AND",
        }
        if "inicio_ajustes" not in self.request.session:
            self.request.session["inicio_ajustes"] = ajustes_default.copy()
        else:
            for key, val in ajustes_default.items():
                self.request.session["inicio_ajustes"].setdefault(key, val)

    def crear_grupos_nuevos_del_admin(self):
        usuario = self.request.user
        ids_objetivo = set(
            Grupo.objects.filter(
                Q(usuario=usuario) | Q(usuario__perfil__rol="admin")
            ).values_list("id", flat=True)
        )  # que registro sea de admin o de usuario
        ids_existentes = set(
            UsuarioGrupo.objects.filter(usuario=usuario).values_list(
                "grupo_id", flat=True
            )
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

    def crear_palabras_nuevas_del_admin(self):
        usuario = self.request.user
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

    def get_user_groups_list(self):
        usuario = self.request.user
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

    def get_context_data(self, **kwargs):
        usuario = self.request.user
        self.asegurar_ajustes_sesion()
        ajustes = self.request.session["inicio_ajustes"]

        self.crear_palabras_nuevas_del_admin()
        self.crear_grupos_nuevos_del_admin()

        context = super().get_context_data(**kwargs)
        context["href_estudio"] = reverse_lazy("estudio")

        context["estudio_url"] = reverse_lazy("preparar_estudio")

        # __ Grupos_ajustes
        context["filtros_grupos"] = [
            {
                "text": filtro,
                "id": filtro + " (grupos)",
                "is_active": ajustes.get(filtro + " (grupos)", False),
                "url": reverse("toggle_filtro"),
            }
            for filtro in [
                "Elegidos",
                "Creados por mí",
                "Por completar",
                "Con estrella",
            ]
        ]
        context["select_orden_url"] = reverse("toggle_orden_select")
        orden_opciones = ("Creación", "Nombre", "Progreso", "Reciente")
        context["orden_opciones"] = orden_opciones
        orden_elegido = ajustes.get("orden_elegido", orden_opciones[0])
        context["orden_elegido"] = orden_elegido
        context["descendente_url"] = reverse("toggle_descendente")
        descendente = ajustes.get("descendente", False)
        context["on_descendente"] = descendente

        # __ Grupos_lista
        context["check_url"] = reverse("toggle_estudiando")
        context["estrella_url"] = reverse("toggle_estrella_grupo")

        grupos = self.get_user_groups_list()

        buscar_grupo_input = (
            self.request.GET.get("buscar_grupo", "").strip().lower()
        )  # search
        context["buscar_grupo_input"] = buscar_grupo_input
        if buscar_grupo_input:
            grupos = [g for g in grupos if buscar_grupo_input in g["text"].lower()]

        grupos_elegidos = [g for g in grupos if g["estudiando"]]
        if ajustes.get("Creados por mí (grupos)"):
            grupos = [g for g in grupos if g["autor"] == usuario.username]
        if ajustes.get("Por completar (grupos)"):
            grupos = [g for g in grupos if g["progreso"] < 100]
        if ajustes.get("Con estrella (grupos)"):
            grupos = [g for g in grupos if g["estrella"]]
        if ajustes.get("Elegidos (grupos)"):
            grupos = grupos_elegidos

        if orden_elegido == "Progreso":
            grupos.sort(key=lambda g: g["progreso"], reverse=descendente)
        elif orden_elegido == "Reciente":
            grupos.sort(
                key=lambda g: g["ultima_modificacion"], reverse=not descendente
            )  # porque de más reciente a menos reciente le pongo el not
        elif orden_elegido == "Nombre":
            grupos.sort(key=lambda g: g["text"].lower(), reverse=descendente)
        elif orden_elegido == "Creación":
            grupos.sort(key=lambda g: g["id"], reverse=descendente)  # !! ojo

        context["grupos"] = grupos

        # __ Preguntas
        context["idioma_preguntas_url"] = reverse("toggle_idioma_preguntas")
        idioma_preguntas_opciones = ("Original", "Significados", "Cualquiera")
        context["idioma_preguntas_opciones"] = idioma_preguntas_opciones
        context["idioma_preguntas_elegido"] = self.request.session.get(
            "idioma_preguntas_elegido", idioma_preguntas_opciones[0]
        )
        context["aleatorio_url"] = reverse("toggle_aleatorio")
        context["is_aleatorio"] = ajustes.get("aleatorio", False)

        # __ Filtros
        context["filtros_palabras_url"] = reverse("toggle_filtros_palabras")
        context["on_filtros_palabras"] = ajustes.get("filtros_palabras") == "OR"
        filtros_palabras = [
            {
                "text": filtro,
                "id": filtro + " (palabras)",
                "is_active": ajustes.get(filtro + " (palabras)", False),
                "url": reverse("toggle_filtro"),
            }
            for filtro in [
                "Creadas por mí",
                "Por completar",
                "Con estrella",
            ]
        ]
        context["filtros_palabras"] = filtros_palabras

        context["filtros_etiquetas_url"] = reverse("toggle_filtros_etiquetas_switch")
        etiquetas_switch_value = ajustes.get("filtros_etiquetas") == "OR"
        context["on_filtros_etiquetas"] = etiquetas_switch_value

        tags = []
        tags_objects = Etiqueta.objects.filter(
            Q(usuario=usuario) | Q(usuario__perfil__rol="admin")
        ).order_by("etiqueta")
        open_collapse = [etiquetas_switch_value]

        for tag in tags_objects:
            active = ajustes.get(f"{tag.etiqueta} (etiqueta)", False)
            tags.append(
                {
                    "text": tag.etiqueta,
                    "id": f"{tag.etiqueta} (etiqueta)",
                    "is_active": active,
                    "url": reverse("toggle_filtro"),
                }
            )
            open_collapse.append(active)

        context["tags"] = tags
        context["is_open_collapse"] = any(open_collapse)

        context["cantidad_palabras"] = len(get_palabras_a_estudiar(usuario, ajustes))
        cantidad_grupos_elegidos = len(grupos_elegidos)
        if cantidad_grupos_elegidos == 1:
            context["cantidad_grupos"] = f"{cantidad_grupos_elegidos} elegido"
        else:
            context["cantidad_grupos"] = f"{cantidad_grupos_elegidos} elegidos"

        print(dict(self.request.session))

        return context

    def is_mobile(request):
        user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
        return user_agent in set("mobile", "android", "iphone", "ipad")


class SesionView(LoginRequiredMixin, TemplateView):
    template_name = "study/sesion.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user

        index = self.request.session.get("index_palabra_pregunta", 0)
        palabras_ids = self.request.session.get("palabras_a_estudiar", [])
        palabra_id = self.request.session.get("palabra_actual")
        palabras_contestadas = self.request.session.get("palabras_contestadas", {})
        palabras_correctas = self.request.session.get("palabras_correctas", {})

        palabra_obj = get_object_or_404(Palabra, id=palabra_id)
        is_kanji = palabra_obj.palabra_etiquetas.filter(
            etiqueta__etiqueta="Kanji"
        ).exists()
        pregunta_lenguaje = self.request.session.get(
            "idioma_preguntas_elegido", "Original"
        )
        palabra_obj.set_pregunta_respuesta(pregunta_lenguaje, usuario, is_kanji)

        pregunta_list = palabra_obj.pregunta
        if len(pregunta_list) > 1:
            lectura_pregunta = f"{str(pregunta_list[1])}"
        else:
            lectura_pregunta = None

        etiquetas_list = palabra_obj.etiquetas_objetos(usuario)
        etiquetas_id_list = [e.etiqueta.id for e in etiquetas_list]
        new_etiquetas_list = Etiqueta.objects.filter(
            (Q(usuario=usuario) | Q(usuario__perfil__rol="admin"))
            & ~Q(id__in=etiquetas_id_list)
        ).order_by("etiqueta")
        new_etiquetas_str = [e.etiqueta for e in new_etiquetas_list]
        new_etiquetas_id = [e.id for e in new_etiquetas_list]
        new_etiquetas_list = dict(zip(new_etiquetas_str, new_etiquetas_id))
        self.request.session["new_etiquetas"] = new_etiquetas_list

        palabra_dict = {
            "id": palabra_id,
            "is_kanji": is_kanji,
            "palabra": palabra_obj.palabra,
            "significados": palabra_obj.significados_list(usuario),
            "lecturas": palabra_obj.lecturas_list(usuario),
            "notas": palabra_obj.notas_list(usuario),
            "etiquetas": palabra_obj.etiquetas_list(usuario),
            "progreso": palabra_obj.palabra_usuarios.get(
                usuario=self.request.user
            ).progreso,
            "estrella": palabra_obj.palabra_usuarios.get(
                usuario=self.request.user
            ).estrella,
            "pregunta": str(pregunta_list[0]),
            "lecturas_pregunta": lectura_pregunta,
        }

        self.request.session["respuestas"] = palabra_obj.respuestas

        context["palabra"] = palabra_dict
        context["palabra_contestada"] = palabras_contestadas[palabra_id]
        context["palabra_correcta"] = palabras_correctas[palabra_id]
        context["index"] = index + 1
        context["index_porcentaje"] = ((index + 1) / len(palabras_ids)) * 100
        context["cambiar_pregunta_url"] = reverse_lazy("cambiar_pregunta")
        context["cambiar_progreso_url"] = reverse_lazy("cambiar_progreso")
        context["checar_pregunta_url"] = reverse("checar_pregunta")
        context["estrella_url"] = reverse("toggle_estrella_palabra")

        context["agregar_significado"] = reverse("agregar_significado")
        context["agregar_lectura"] = reverse("agregar_lectura")
        context["agregar_nota"] = reverse("agregar_nota")
        context["agregar_etiqueta"] = reverse("agregar_etiqueta")
        context["nuevas_etiquetas"] = new_etiquetas_str

        print(dict(self.request.session))
        return context

    def is_mobile(request):
        user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
        return user_agent in set("mobile", "android", "iphone", "ipad")
