from django.shortcuts import render
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from tags.models import Etiqueta
from groups.models import Grupo


class HomeView(TemplateView):
    template_name = "study/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["href_estudio"] = reverse_lazy("estudio")
        context["preguntas"] = ("Original", "Traducción", "Cualquiera")
        context["orden"] = ("Nombre", "Progreso")
        context["tags"] = Etiqueta.objects.all().order_by("etiqueta")
        context["grupos"] = Grupo.objects.all().order_by("grupo")
        return context

    def is_mobile(request):
        user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
        return any(m in user_agent for m in ["mobile", "android", "iphone", "ipad"])
