from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.shortcuts import redirect, get_object_or_404
import random

from tags.models import Etiqueta
from groups.models import Grupo, UsuarioGrupo, GrupoPalabra
from dictionary.models import Palabra
from progress.models import UsuarioPalabra


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
def toggle_estrella(request):
    grupo_id = request.POST.get("swap_id")
    user = request.user
    entry = get_object_or_404(UsuarioGrupo, usuario=user, grupo_id=grupo_id)
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
    ajustes = request.session.get("inicio_ajustes", {})
    value = request.POST.get("select")
    if value:
        ajustes["idioma_preguntas"] = value
        request.session["inicio_ajustes"] = ajustes
    return redirect(request.META.get("HTTP_REFERER", "/"))


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
            ~Q(palabra_usuarios__usuario=usuario, palabra_usuarios__progreso=100)
        )

    if ajustes.get("Con estrella (palabras)"):
        condiciones.append(
            Q(palabra_usuarios__usuario=usuario, palabra_usuarios__estrella=True)
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


@require_POST
@login_required
def preparar_estudio(request):
    ajustes = request.session.get("inicio_ajustes", {})
    usuario = request.user

    palabras_qs = get_palabras_a_estudiar(usuario, ajustes)
    if not palabras_qs:
        messages.warning(
            request, "No hay palabras que estudiar con los filtros actuales."
        )
        return redirect(request.META.get("HTTP_REFERER", "/"))
    palabras_id = [palabra.id for palabra in palabras_qs]
    request.session["palabras_a_estudiar"] = palabras_id
    return redirect("estudio")


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
            "index_palabra_pregunta": 0,
            "contestada": False,
            "correcta": False,
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
                    "ultima_modificacion": ug.grupo.ultima_modificacion,
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
        context["estrella_url"] = reverse("toggle_estrella")

        grupos = self.get_user_groups_list()
        if ajustes.get("Creados por mí (grupos)"):
            grupos = [g for g in grupos if g["autor"] == usuario.username]
        if ajustes.get("Por completar (grupos)"):
            grupos = [g for g in grupos if g["progreso"] < 100]
        if ajustes.get("Con estrella (grupos)"):
            grupos = [g for g in grupos if g["estrella"]]
        if ajustes.get("Elegidos (grupos)"):
            grupos = [g for g in grupos if g["estudiando"]]

        buscar_grupo_input = (
            self.request.GET.get("buscar_grupo", "").strip().lower()
        )  # search
        context["buscar_grupo_input"] = buscar_grupo_input
        if buscar_grupo_input:
            grupos = [g for g in grupos if buscar_grupo_input in g["text"].lower()]

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
        idioma_preguntas_opciones = ("Original", "Traducción", "Cualquiera")
        context["idioma_preguntas_opciones"] = idioma_preguntas_opciones
        context["idioma_preguntas"] = ajustes.get(
            "idioma_preguntas", idioma_preguntas_opciones[0]
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

        print(dict(ajustes))

        return context

    def is_mobile(request):
        user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
        return any(m in user_agent for m in ["mobile", "android", "iphone", "ipad"])


class PreguntaView(LoginRequiredMixin, TemplateView):
    template_name = "study/pregunta.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        index = self.request.session.get("index_palabra_pregunta", 0)
        palabra_ids = self.request.session.get("palabras_a_estudiar", [])
        palabra_obj = get_object_or_404(Palabra, id=palabra_ids[index])

        context["pregunta"] = palabra_obj.palabra
        context["index"] = 20
        context["progreso"] = palabra_obj.palabra_usuarios.get(
            usuario=self.request.user
        ).progreso
        context["estrella"] = palabra_obj.palabra_usuarios.get(
            usuario=self.request.user
        ).estrella
        return context

    def is_mobile(request):
        user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
        return any(m in user_agent for m in ["mobile", "android", "iphone", "ipad"])
