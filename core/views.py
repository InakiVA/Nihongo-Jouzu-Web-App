from django.shortcuts import render
from django.db.models import Q
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

import core.utils as ut

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
        context["buscando"] = search_input
        search_input_list = ut.set_alternate_inputs([search_input])
        owner_q = Q(usuario=usuario) | Q(usuario__perfil__rol="admin")
        if ajustes_buscar.get("buscando_tipo", "palabra") == "palabra":
            exact_results = Palabra.objects.filter(
                owner_q,
                Q(palabra__in=search_input_list)
                | Q(significados__significado__in=search_input_list)
                | Q(lecturas__lectura__in=search_input_list),
            ).distinct()
            related_queries = Q()
            for term in search_input_list:
                related_queries |= (
                    Q(palabra__istartswith=term)
                    | Q(significados__significado__istartswith=term)
                    | Q(lecturas__lectura__istartswith=term)
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
                )
            contains_results = (
                Palabra.objects.filter(owner_q, related_queries)
                .exclude(id__in=exact_results)
                .exclude(id__in=startswith_results)
                .distinct()
            )

            results = (
                list(exact_results) + list(startswith_results) + list(contains_results)
            )

            index = ajustes_buscar.get("index_palabra", 0)
            index = ut.bound_page_index(index, len(results))
            ajustes_buscar["index_palabra"] = index

            palabras_list = []
            related_list = []
            for i in range(index * 10, min(len(results), index * 10 + 10)):
                palabra = results[i]
                value = {
                    "id": palabra.id,
                    "palabra": palabra.palabra,
                    "significados": palabra.significados_str(usuario),
                    "lecturas": palabra.lecturas_str(usuario),
                    "notas": palabra.notas_str(usuario),
                    "etiquetas": palabra.etiquetas_list(usuario),
                    "grupos": palabra.grupos_str(usuario),
                    "progreso": palabra.palabra_usuarios.get(
                        usuario=self.request.user
                    ).progreso,
                    "estrella": palabra.palabra_usuarios.get(
                        usuario=self.request.user
                    ).estrella,
                }
                if i < len(exact_results):
                    palabras_list.append(value)
                else:
                    related_list.append(value)

            index = ajustes_buscar.get("page_index", 0)

            context["palabras_list"] = palabras_list
            context["palabras_related"] = related_list
            context["palabra_url"] = reverse_lazy("elegir_palabra")

        return context
