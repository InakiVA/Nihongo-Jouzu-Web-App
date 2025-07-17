from django.shortcuts import render
from django.views.generic import TemplateView
from django.urls import reverse_lazy


class HomeView(TemplateView):
    template_name = "study/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["href_estudio"] = reverse_lazy("estudio")
        context["value"] = 5  # esto es para testear radial progress
        context["value2"] = 35
        context["value3"] = 75
        context["value4"] = 100
        context["rows"] = [
            {"text": "Group1", "progress": 5},
            {"text": "Group2", "progress": 50},
            {"text": "nombrelarguisimowtf", "progress": 75},
            {"text": "Group4", "progress": 100},
        ]
        context["rows2"] = [
            {"text": "F", "progress": 5},
            {"text": "G", "progress": 50},
        ]
        return context

    def is_mobile(request):
        user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
        return any(m in user_agent for m in ["mobile", "android", "iphone", "ipad"])
