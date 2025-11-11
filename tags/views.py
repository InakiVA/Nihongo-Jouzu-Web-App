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

from django.db.models import Q


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "tags/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user

        tag_colors = [
            "main",
            "0",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "neutral",
        ]

        tag_obj_list = Etiqueta.objects.filter(
            Q(usuario=usuario) | Q(usuario__perfil__rol="admin")
        ).order_by("etiqueta", "color")
        tag_list = [tag.etiqueta_dict() for tag in tag_obj_list]
        for tag_dict in tag_list:
            tag_dict["editable"] = tag_dict["creador"] == usuario

        context["tag_colors"] = tag_colors
        context["tag_list"] = tag_list
        context["default_color"] = "neutral"

        context["crear_etiqueta_url"] = reverse_lazy("crear_etiqueta")
        context["editar_etiqueta_url"] = reverse_lazy("update_etiqueta")
        context["editar_color_url"] = reverse_lazy("update_color")
        context["eliminar_etiqueta_url"] = reverse_lazy("eliminar_etiqueta")
        return context

    def is_mobile(request):
        user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
        return any(m in user_agent for m in ["mobile", "android", "iphone"])
