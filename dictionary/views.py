from django.shortcuts import render
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin


class DictionaryView(LoginRequiredMixin, TemplateView):
    template_name = "dictionary/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["href_diccionario"] = reverse_lazy("diccionario")
        context["value"] = 5  # esto es para testear radial progress
        context["value2"] = 35
        context["value3"] = 75
        context["value4"] = 100
        context["rows"] = [
            {"text": "Group1", "progress": 0},
            {"text": "Group2", "progress": 50},
            {"text": "nombrelarguisimowtf", "progress": 75},
            {"text": "Group4", "progress": 100},
        ]
        context["rows2"] = [
            {"text": "F", "progress": 5},
            {"text": "G", "progress": 50},
        ]
        context["options"] = [
            {
                "value": "light",
                "label": "Light mode is very long for this option text isn't it honey",
            },
            {"value": "dark", "label": "Dark mode"},
            {"value": "system", "label": "System"},
        ]
        lecturas = [
            "は",
            "ひ",
            "ふ",
            "へ",
            "ほ",
            "ahora",
            "unaas",
            "bieeen",
            "largas",
            "para que amarre parejo",
            "y ver si se elimina",
        ]
        context["lecturas"] = ", ".join(lecturas)
        significados = [
            "este significado es muy largo",
            "pero bueno ya qué se le va a hacer",
            "no me queda de otra más que testear con textos bien largos",
        ]
        context["significados"] = ", ".join(significados)
        tags = (
            "Kanji",
            "JLPT N5",
            "Adjetivo",
            "Muy largo tag largo",
            "Kanji",
            "JLPT N5",
            "Adjetivo",
            "Muy largo tag largo",
            "Kanji",
            "JLPT N5",
            "Adjetivo",
            "Muy largo tag largo",
            "Kanji",
            "JLPT N5",
            "Adjetivo",
            "Muy largo tag largo",
            "Kanji",
            "JLPT N5",
            "Adjetivo",
            "Muy largo tag largo",
        )
        context["tags"] = tags
        context["side_to_side"] = "Kanji" in tags

        return context

    """def is_mobile(request):
        user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
        return any(m in user_agent for m in ["mobile", "android", "iphone", "ipad"])"""
