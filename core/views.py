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

        search_input = self.request.GET.get("search")
        search_input_list = ut.set_alternate_inputs([search_input])
        print(search_input_list)
        if self.request.session.get("buscando_tipo", "palabra") == "palabra":
            results = Palabra.objects.filter(palabra__in=search_input_list)
            print(results)

            context["palabras_list"] = results

        return context
