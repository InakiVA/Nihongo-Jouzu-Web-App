from django.shortcuts import render
from django.db.models import Q
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from dictionary.models import Palabra, Significado, Lectura
from progress.models import UsuarioPalabra
from groups.models import Grupo

import core.utils as ut


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
        context["palabras_relacionadas_url"] = reverse_lazy("elegir_palabra")

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
        context["grupos_checks_url"] = reverse_lazy("toggle_palabra_en_grupo")

        return context


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "dictionary/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user

        context["crear_palabra_url"] = reverse_lazy("crear_palabra")
        context["toggle_modal_url"] = reverse_lazy("toggle_modal")

        ajustes_palabras = self.request.session.get("ajustes_palabras", {})

        context["intentado"] = ajustes_palabras.get("intentado", False)

        palabras = Palabra.objects.filter(
            (Q(usuario=usuario) | Q(usuario__perfil__rol="admin"))
        )
        index = ajustes_palabras.get("page_index", 0)
        index = ut.bound_page_index(index, len(palabras))
        ajustes_palabras["page_index"] = index
        palabras_list = []
        for palabra in palabras[index * 10 : min(len(palabras), index * 10 + 10)]:
            palabras_list.append(
                {
                    "id": palabra.id,
                    "palabra": palabra.palabra,
                    "significados": palabra.significados_str(usuario),
                    "lecturas": palabra.lecturas_str(usuario),
                    "notas": palabra.notas_str(usuario),
                    "etiquetas": palabra.etiquetas_list(usuario),
                    "grupos": palabra.grupos_str(usuario),
                    "progreso": palabra.palabra_usuarios.get(
                        usuario=self.request.user
                    ).progreso,
                    "estrella": palabra.palabra_usuarios.get(
                        usuario=self.request.user
                    ).estrella,
                }
            )
        context["palabras_list"] = palabras_list
        context["index"] = index + 1
        context["cambiar_pagina_url"] = reverse_lazy("cambiar_pagina")

        context["palabra_url"] = reverse_lazy("elegir_palabra")
        context["ajustes_palabras"] = ajustes_palabras
        self.request.session["ajustes_palabras"] = ajustes_palabras

        return context

    def is_mobile(request):
        user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
        return any(m in user_agent for m in ["mobile", "android", "iphone"])
