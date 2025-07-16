from django.shortcuts import render
from django.views.generic import TemplateView
from django.urls import reverse_lazy


class HomeView(TemplateView):
    template_name = "study/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["href_estudio"] = reverse_lazy("estudio")
        return context
