from django.shortcuts import render
from django.views.generic import TemplateView
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from dictionary.models import Palabra, Significado, Lectura, Nota


@require_POST
@login_required
def toggle_modal(request):
    modal_settings = request.session.get("ajustes_modal", {})
    open_modal = modal_settings.get("open_modal", False)
    modal_settings["open_modal"] = not open_modal
    modal_settings["intentado"] = False
    request.session["ajustes_modal"] = modal_settings
    return redirect(request.META.get("HTTP_REFERER", "/"))


@require_POST
@login_required
def crear_palabra(request):
    modal_settings = request.session.get("ajustes_modal")
    modal_settings["intentado"] = True
    palabra_value = request.POST.get("palabra_nueva")
    significado_value = request.POST.get("significado_nuevo")
    lectura_value = request.POST.get("lectura_nueva")
    if False == all([palabra_value, significado_value, lectura_value]):
        for key, value in zip(
            ["palabra_valida", "significado_valido", "lectura_valida"],
            [palabra_value, significado_value, lectura_value],
        ):
            modal_settings[key] = value
        request.session["ajustes_modal"] = modal_settings
        return redirect(request.META.get("HTTP_REFERER", "/"))
    for key, value in zip(
        ["palabra_valida", "significado_valido", "lectura_valida"],
        ["", "", ""],
    ):
        modal_settings[key] = value
    modal_settings["open_modal"] = not modal_settings["open_modal"]
    user = request.user
    palabra_obj = Palabra.objects.create(usuario=user, palabra=palabra_value)
    print(palabra_obj.id)  # ** funciona, referir a página de detalles

    request.session["ajustes_modal"] = modal_settings
    return redirect(request.META.get("HTTP_REFERER", "/"))


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "dictionary/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["href_palabras"] = reverse_lazy("palabras")
        context["crear_palabra_url"] = reverse("crear_palabra")
        context["toggle_modal_url"] = reverse("toggle_modal")

        ajustes_modal = self.request.session.get("ajustes_modal")
        context["ajustes_modal"] = ajustes_modal
        context["intentado"] = ajustes_modal.get("intentado", False)

        print(dict(self.request.session))
        return context

    def is_mobile(request):
        user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
        return any(m in user_agent for m in ["mobile", "android", "iphone"])
