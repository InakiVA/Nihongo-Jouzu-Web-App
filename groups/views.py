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

        context["crear_grupo_url"] = reverse_lazy("crear_grupo")

        index = ajustes_grupos.get("page_index", 0)
        index = ut.bound_page_index(index, len(grupos))
        ajustes_grupos["page_index"] = index
        context["index"] = index + 1

        grupos_list = grupos[index * 10 : min(len(grupos), index * 10 + 10)]

        context["ajustes_grupos"] = ajustes_grupos

        context["grupos_list"] = grupos_list
        context["grupo_url"] = reverse_lazy("elegir_grupo")
        context["grupo_estrella_url"] = reverse_lazy("toggle_estrella_grupo")

        pages_list = ut.create_pages_list(index, len(grupos))
        context["show_pages_list"] = len(pages_list) > 1
        context["pages_list"] = pages_list

        context["cambiar_pagina_url"] = reverse_lazy("cambiar_pagina_grupos")

        context["intentado"] = ajustes_grupos.get("intentado", False)

        self.request.session["ajustes_grupos"] = ajustes_grupos
        return context

    def is_mobile(request):
        user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
        return any(m in user_agent for m in ["mobile", "android", "iphone"])


class EditView(LoginRequiredMixin, TemplateView):
    template_name = "groups/edit.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user

        grupo_id = self.request.session["grupo_actual"]
        grupo_obj = get_object_or_404(Grupo, id=grupo_id)

        grupo = {
            "id": grupo_id,
            "grupo": grupo_obj.grupo,
            "descripcion": grupo_obj.descripcion,
            "editable": grupo_obj.usuario == usuario,
        }

        context["grupo"] = grupo

        context["detalles_url"] = reverse_lazy("detalles_grupo")

        context["update_grupo"] = reverse_lazy("update_grupo")
        context["update_descripcion"] = reverse_lazy("update_descripcion")

        context["delete_grupo"] = reverse_lazy("delete_grupo")

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
            "creador": ug.grupo.usuario,
            "editable": ug.grupo.usuario == usuario,
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
                    "palabra": palabra.palabra,
                    "lecturas": palabra.lecturas_str(usuario),
                    "significados": palabra.significados_str(usuario),
                    "etiquetas": palabra.etiquetas_list(usuario),
                    "progreso": usuario_palabra.progreso,
                    "estrella": usuario_palabra.estrella,
                    "checked": True,
                }
            )

        context["palabras"] = palabras
        context["grupo_tiene_palabra_url"] = reverse_lazy("toggle_grupo_tiene_palabra")
        context["len_palabras"] = len(palabras)
        context["palabra_url"] = reverse_lazy("elegir_palabra")

        context["editar_url"] = reverse_lazy("editar_grupo")

        context["buscar_palabras"] = reverse_lazy("buscar_filtrar_grupo_actual")

        return context

    def is_mobile(request):
        user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
        return any(m in user_agent for m in ["mobile", "android", "iphone"])
