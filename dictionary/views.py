from django.shortcuts import render
from django.db.models import Q
from django.views.generic import TemplateView
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from dictionary.models import Palabra, Significado, Lectura
from progress.models import UsuarioPalabra
from groups.models import Grupo


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
    UsuarioPalabra.objects.create(usuario=user, palabra=palabra_obj)
    Significado.objects.create(
        significado=significado_value, palabra=palabra_obj, usuario=user
    )
    Lectura.objects.create(lectura=lectura_value, palabra=palabra_obj, usuario=user)
    request.session["palabra_actual"] = palabra_obj.id
    request.session["ajustes_modal"] = modal_settings
    return redirect("detalles")


class DetailView(LoginRequiredMixin, TemplateView):
    template_name = "dictionary/details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        palabra_id = self.request.session.get("palabra_actual", "")
        palabra_obj = get_object_or_404(Palabra, id=palabra_id)

        palabra_dict = {
            "id": palabra_id,
            "palabra": palabra_obj.palabra,
            "significados": palabra_obj.significados_str(usuario),
            "lecturas": palabra_obj.lecturas_str(usuario),
            "notas": palabra_obj.notas_str(usuario),
            "etiquetas": palabra_obj.etiquetas_list(usuario),
            "grupos": palabra_obj.grupos_str(usuario),
            "progreso": palabra_obj.palabra_usuarios.get(
                usuario=self.request.user
            ).progreso,
            "estrella": palabra_obj.palabra_usuarios.get(
                usuario=self.request.user
            ).estrella,
        }
        context["palabra"] = palabra_dict

        palabras_relacionadas = palabra_obj.palabras_relacionadas(usuario)
        palabras_relacionadas_dict_list = []
        for palabra in palabras_relacionadas:
            palabras_relacionadas_dict_list.append(
                {
                    "id": palabra.id,
                    "palabra": palabra.palabra,
                    "significados": palabra.significados_str(usuario),
                    "lecturas": palabra.lecturas_str(usuario),
                    "etiquetas": palabra.etiquetas_list(usuario),
                    "notas": palabra.notas_str(usuario),
                    "progreso": palabra.palabra_usuarios.get(
                        usuario=self.request.user
                    ).progreso,
                    "estrella": palabra.palabra_usuarios.get(
                        usuario=self.request.user
                    ).estrella,
                }
            )
        context["palabras_relacionadas"] = palabras_relacionadas_dict_list

        grupos_usuario = list(Grupo.objects.filter(usuario=usuario))
        grupos_de_palabra_de_usuario = set(
            Grupo.objects.filter(usuario=usuario, grupo_palabras__palabra=palabra_obj)
        )

        grupos_checks = []
        for grupo in grupos_usuario:
            grupos_checks.append(
                {
                    "id": grupo.id,
                    "text": grupo.grupo,
                    "is_selected": grupo in grupos_de_palabra_de_usuario,
                }
            )
        context["grupos_checks"] = grupos_checks
        context["grupos_checks_url"] = reverse("toggle_palabra_en_grupo")

        return context


class SearchView(LoginRequiredMixin, TemplateView):
    template_name = "dictionary/search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "dictionary/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["crear_palabra_url"] = reverse("crear_palabra")
        context["toggle_modal_url"] = reverse("toggle_modal")

        ajustes_modal = self.request.session.get("ajustes_modal", {})
        context["ajustes_modal"] = ajustes_modal
        context["intentado"] = ajustes_modal.get("intentado", False)

        print(dict(self.request.session))
        return context

    def is_mobile(request):
        user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
        return any(m in user_agent for m in ["mobile", "android", "iphone"])
