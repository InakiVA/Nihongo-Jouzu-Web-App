from django.shortcuts import render
from django.views.generic import TemplateView
from django.urls import reverse_lazy


class UserView(TemplateView):
    template_name = "accounts/user.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["href_usuario"] = reverse_lazy("usuario")

        return context

    def is_mobile(request):
        user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
        return any(m in user_agent for m in ["mobile", "android", "iphone", "ipad"])
