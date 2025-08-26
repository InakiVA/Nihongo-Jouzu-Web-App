from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from tags.models import Etiqueta
from groups.models import Grupo, UsuarioGrupo
from dictionary.models import Palabra
from progress.models import UsuarioPalabra

import core.operations as c_op
import core.utils as ut


class GroupsView(LoginRequiredMixin, TemplateView):
    template_name = "groups/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user

        grupos = c_op.get_user_groups_list(usuario)

        ajustes_grupos = self.request.session.get("ajustes_grupos", {})

        index = ajustes_grupos.get("page_index", 0)
        index = ut.bound_page_index(index, len(grupos))
        ajustes_grupos["page_index"] = index
        context["index"] = index + 1

        grupos_list = grupos[index * 10 : min(len(grupos), index * 10 + 10)]

        context["grupos_list"] = grupos_list
        context["grupo_url"] = reverse_lazy("elegir_grupo")
        context["grupo_estrella_url"] = reverse_lazy("toggle_estrella_grupo")

        max_page = len(grupos) // 10

        pages_list = ut.create_pages_list(index, max_page)
        context["show_pages_list"] = len(pages_list) > 1
        context["pages_list"] = pages_list

        context["cambiar_pagina_url"] = reverse_lazy("cambiar_pagina_grupos")

        context["intentado"] = ajustes_grupos.get("intentado", False)

        return context

    def is_mobile(request):
        user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
        return any(m in user_agent for m in ["mobile", "android", "iphone"])


class DetailView(LoginRequiredMixin, TemplateView):
    template_name = "groups/details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user

        grupo_id = self.request.session["grupo_actual"]
        ug = get_object_or_404(
            UsuarioGrupo.objects.select_related("grupo").prefetch_related(
                "grupo__grupo_palabras__palabra__palabra_usuarios"
            ),
            usuario=usuario,
            grupo_id=grupo_id,
        )

        grupo = {
            "id": grupo_id,
            "grupo": ug.grupo.grupo,
            "descripcion": ug.grupo.descripcion,
            "progreso": int(ug.progreso),
            "estrella": ug.estrella,
        }

        context["grupo"] = grupo
        context["grupo_estrella_url"] = reverse_lazy("toggle_estrella_grupo")

        palabras_obj_list = [gp.palabra for gp in ug.grupo.grupo_palabras.all()]

        palabras = []
        for palabra in palabras_obj_list:
            usuario_palabra = get_object_or_404(
                UsuarioPalabra, palabra_id=palabra.id, usuario=usuario
            )
            palabras.append(
                {
                    "id": palabra.id,
                    "text": palabra.palabra,
                    "progreso": usuario_palabra.progreso,
                    "estrella": usuario_palabra.estrella,
                    "checked": True,
                }
            )

        context["palabras"] = palabras
        context["palabra_estrella_url"] = reverse_lazy("toggle_estrella_palabra")
        context["len_palabras"] = len(palabras)

        return context

    def is_mobile(request):
        user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
        return any(m in user_agent for m in ["mobile", "android", "iphone"])
