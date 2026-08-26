from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from groups.models import Grupo
from dictionary.models import Palabra

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


class EditView(LoginRequiredMixin, TemplateView):
    template_name = "groups/edit.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user

        grupo_id = self.request.session["grupo_actual"]
        grupo_obj = get_object_or_404(Grupo, id=grupo_id)

        grupo = grupo_obj.grupo_dict(usuario=usuario)

        context["grupo"] = grupo

        context["detalles_url"] = reverse_lazy("detalles_grupo")

        context["update_grupo"] = reverse_lazy("update_grupo")
        context["update_descripcion"] = reverse_lazy("update_descripcion")

        context["delete_grupo"] = reverse_lazy("delete_grupo")

        return context


class DetailView(LoginRequiredMixin, TemplateView):
    template_name = "groups/details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        grupo_id = self.request.session["grupo_actual"]
        grupo_obj = get_object_or_404(Grupo, id=grupo_id)
        context["grupo"] = grupo_obj.grupo_dict(usuario=usuario)

        # ------------------------------------------------------------
        # PAGINATION STATE (similar to HomeView)
        # ------------------------------------------------------------
        ajustes = self.request.session.get("ajustes_palabras_en_grupo", {})
        editando = ajustes.get("editando", False)

        context["grupo_tiene_palabra_url"] = reverse_lazy("toggle_grupo_tiene_palabra")
        context["palabra_url"] = reverse_lazy("elegir_palabra")
        context["editar_url"] = reverse_lazy("editar_grupo")

        palabras = (
            Palabra.objects.filter(palabra_grupos__grupo_id=grupo_id)
            .distinct()
            .order_by("id")
        )
        total_palabras = len(palabras)

        if grupo_id != ajustes.get("last_grupo_id", None):
            ajustes["page_index"] = 0  # reset page index if different group
            ajustes["last_grupo_id"] = grupo_id
            editando = False
            ajustes["editando"] = editando

        index = ajustes.get("page_index", 0)
        index = ut.bound_page_index(index, total_palabras)
        context["index"] = index + 1
        start = index * 10
        end = min(total_palabras, start + 10)

        palabras_list = []

        for palabra in palabras[start:end]:
            d = palabra.palabra_dict(usuario)
            d["checked"] = True
            palabras_list.append(d)
        context["palabras"] = palabras_list

        # ------------------------------------------------------------
        # PAGINATION UI
        # ------------------------------------------------------------

        ajustes["page_index"] = index
        context["grupo_estrella_url"] = reverse_lazy("toggle_estrella_grupo")

        if total_palabras == 0:
            context["range"] = "No hay palabras para mostrar"
        else:
            context["range"] = f"{start + 1} - {end} de {total_palabras}"

        # Create pagination list same as HomeView (use ut.create_pages_list)
        pages_list = ut.create_pages_list(index, total_palabras)
        context["pages_list"] = pages_list
        context["show_pages_list"] = len(pages_list) > 1

        # URL for pagination actions
        context["cambiar_pagina_url"] = reverse_lazy("cambiar_pagina_palabras_en_grupo")
        context["editar_palabras_url"] = reverse_lazy("toggle_editar_palabras")
        context["editando"] = editando

        # Save session state
        self.request.session["ajustes_palabras_en_grupo"] = ajustes

        return context
