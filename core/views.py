from django.shortcuts import render
from django.db.models import Q
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

import core.utils as ut
import core.components as cp

from dictionary.models import Palabra, Significado, Lectura
from progress.models import UsuarioPalabra
from groups.models import Grupo


class SearchView(LoginRequiredMixin, TemplateView):
    template_name = "core/search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        # ajustes_buscar = {"tipo":"palabra","index_palabra": 0, "index_grupos": 0, "index_etiquetas": 0}
        ajustes_buscar = self.request.session.get("ajustes_buscar", {})
        search_input = self.request.GET.get("search")
        if not search_input:
            context["buscando"] = "No se introdujo nada para buscar"
            return context
        context["buscando"] = f"Buscando {search_input}:"
        resultados = cp.buscar_header(self.request, search_input, usuario)
        palabras_list = resultados[0]
        related_list = resultados[1]
        index = resultados[2]
        pages_list = ut.create_pages_list(index, resultados[3])
        context["show_pages_list"] = len(pages_list) > 1
        context["pages_list"] = pages_list
        context["relacionadas_buscando"] = f"Palabras que contienen {search_input}:"

        context["cambiar_pagina_url"] = reverse_lazy("cambiar_pagina_buscar")

        context["palabras_list"] = palabras_list
        context["palabras_related"] = related_list
        context["palabra_url"] = reverse_lazy("elegir_palabra")

        return context
