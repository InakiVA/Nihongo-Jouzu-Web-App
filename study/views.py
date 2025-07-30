from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.shortcuts import redirect, get_object_or_404

from tags.models import Etiqueta
from groups.models import Grupo, UsuarioGrupo
from dictionary.models import Palabra
from progress.models import UsuarioPalabra


# __ Checkboxes
@require_POST
@login_required
def toggle_aleatorio(request):
    key = "aleatorio_id"
    value = request.session.get(key, False)
    request.session[key] = not value
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
    key = "descendente_id"
    value = request.session.get(key, False)
    request.session[key] = not value
    print(dict(request.session))
    return redirect(request.META.get("HTTP_REFERER", "/"))


@require_POST
@login_required
def toggle_filtros_palabras(request):
    key = "filtros_palabras_switch_id"
    value = request.session.get(key, "AND")
    request.session[key] = "OR" if value == "AND" else "AND"
    return redirect(request.META.get("HTTP_REFERER", "/"))


@require_POST
@login_required
def toggle_filtros_etiquetas_switch(request):
    key = "filtros_etiquetas_switch_id"
    value = request.session.get(key, "AND")
    request.session[key] = "OR" if value == "AND" else "AND"
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


# __ Selects
@require_POST
@login_required
def toggle_orden_select(request):
    value = request.POST.get("select")
    if value:
        request.session["orden_elegido"] = value
    return redirect(request.META.get("HTTP_REFERER", "/"))


@require_POST
@login_required
def toggle_idioma_preguntas(request):
    value = request.POST.get("select")
    if value:
        request.session["idioma_preguntas_elegido"] = value
    return redirect(request.META.get("HTTP_REFERER", "/"))


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "study/home.html"

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
        self.crear_palabras_nuevas_del_admin()
        self.crear_grupos_nuevos_del_admin()
        context = super().get_context_data(**kwargs)
        context["href_estudio"] = reverse_lazy("estudio")

        # __ Grupos_ajustes
        context["select_orden_url"] = reverse("toggle_orden_select")
        orden_opciones = ("Creación", "Nombre", "Progreso", "Reciente")
        context["orden_opciones"] = orden_opciones
        orden_elegido = self.request.session.get("orden_elegido", orden_opciones[0])
        context["orden_elegido"] = orden_elegido
        context["descendente_url"] = reverse("toggle_descendente")
        context["on_descendente"] = self.request.session.get("descendente_id", False)

        # __ Grupos_lista
        context["check_url"] = reverse("toggle_estudiando")
        context["estrella_url"] = reverse("toggle_estrella")

        descendente = self.request.session.get("descendente_id", False)

        grupos = self.get_user_groups_list()

        if orden_elegido == "Progreso":
            grupos.sort(key=lambda g: g["progreso"], reverse=descendente)
        elif orden_elegido == "Reciente":
            grupos.sort(key=lambda g: g["ultima_modificacion"], reverse=descendente)
        elif orden_elegido == "Nombre":
            grupos.sort(key=lambda g: g["text"].lower(), reverse=descendente)
        elif orden_elegido == "Creación":
            grupos.sort(key=lambda g: g["id"], reverse=descendente)  # !! ojo

        context["grupos"] = grupos

        # __ Preguntas
        context["idioma_preguntas_url"] = reverse("toggle_idioma_preguntas")
        idioma_preguntas_opciones = ("Original", "Traducción", "Cualquiera")
        context["idioma_preguntas_opciones"] = idioma_preguntas_opciones
        context["idioma_preguntas_elegido"] = self.request.session.get(
            "idioma_preguntas_elegido", idioma_preguntas_opciones[0]
        )
        context["aleatorio_url"] = reverse("toggle_aleatorio")
        context["is_aleatorio"] = self.request.session.get("aleatorio_id", False)

        # __ Filtros
        context["filtros_palabras_url"] = reverse("toggle_filtros_palabras")

        context["on_filtros_palabras"] = (
            self.request.session.get("filtros_palabras_switch_id") == "OR"
        )

        context["filtros_etiquetas_url"] = reverse("toggle_filtros_etiquetas_switch")
        etiquetas_switch_value = (
            self.request.session.get("filtros_etiquetas_switch_id") == "OR"
        )
        context["on_filtros_etiquetas"] = etiquetas_switch_value
        context["tags"] = Etiqueta.objects.filter(
            Q(usuario=usuario) | Q(usuario__perfil__rol="admin")
        ).order_by("etiqueta")

        context["is_open_collapse"] = any([etiquetas_switch_value])

        return context

    def is_mobile(request):
        user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
        return any(m in user_agent for m in ["mobile", "android", "iphone", "ipad"])
