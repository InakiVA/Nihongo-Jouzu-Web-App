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


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "tags/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user

        tag_colors = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "neutral"]

        tag_obj_list = Etiqueta.objects.filter(usuario=usuario).order_by(
            "color", "etiqueta"
        )
        tag_list = [tag.etiqueta_dict() for tag in tag_obj_list]
        for tag_dict in tag_list:
            tag_dict["editable"] = tag_dict["creador"] == usuario

        context["tag_colors"] = tag_colors
        context["tag_list"] = tag_list
        return context

    def is_mobile(request):
        user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
        return any(m in user_agent for m in ["mobile", "android", "iphone"])
