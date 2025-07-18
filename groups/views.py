from django.shortcuts import render
from django.views.generic import TemplateView
from django.urls import reverse_lazy


class GroupsView(TemplateView):
    template_name = "groups/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["href_grupos"] = reverse_lazy("grupos")

        return context

    def is_mobile(request):
        user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
        return any(m in user_agent for m in ["mobile", "android", "iphone", "ipad"])
