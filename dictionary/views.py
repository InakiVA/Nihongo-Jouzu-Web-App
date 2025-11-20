from django.shortcuts import render
from django.db.models import Q
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from dictionary.models import Palabra, Significado, Lectura
from progress.models import UsuarioPalabra
from groups.models import Grupo
from tags.models import Etiqueta

import core.utils as ut
import core.operations as c_op


class DetailView(LoginRequiredMixin, TemplateView):
    template_name = "dictionary/details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        palabra_id = self.request.session.get("palabra_actual", 0)
        palabra_obj = get_object_or_404(Palabra, id=palabra_id)

        palabra_dict = palabra_obj.palabra_dict(usuario=usuario)
        context["palabra"] = palabra_dict

        palabras_relacionadas = palabra_obj.palabras_relacionadas(usuario)
        palabras_relacionadas_dict_list = []
        for palabra in palabras_relacionadas:
            palabras_relacionadas_dict_list.append(
                palabra.palabra_dict(usuario=usuario)
            )
        context["palabras_relacionadas"] = palabras_relacionadas_dict_list
        context["palabras_relacionadas_url"] = reverse_lazy("elegir_palabra")

        grupos_usuario = c_op.get_user_groups_list(usuario)
        grupos_de_palabra_de_usuario = set(
            Grupo.objects.filter(
                usuario=usuario, grupo_palabras__palabra=palabra_obj
            ).values_list("grupo", flat=True)
        )

        grupos_checks = []
        new_grupos_list = {}
        new_grupos_str = []
        for grupo in grupos_usuario:
            grupo_str = grupo["grupo"]
            if grupo_str in grupos_de_palabra_de_usuario:
                grupos_checks.append(
                    {
                        "id": grupo["id"],
                        "text": grupo["grupo"],
                        "is_selected": True,
                    }
                )
            else:
                new_grupos_list[grupo["grupo"]] = grupo["id"]
                new_grupos_str.append(grupo["grupo"])

        context["nuevos_grupos"] = new_grupos_str
        self.request.session["new_grupos"] = new_grupos_list
        context["agregar_grupo"] = reverse_lazy("agregar_grupo")

        context["grupos_checks"] = grupos_checks
        context["grupos_checks_url"] = reverse_lazy("toggle_palabra_en_grupo")
        context["estrella_url"] = reverse_lazy("toggle_estrella_palabra")
        context["cambiar_progreso_url"] = reverse_lazy("cambiar_progreso")
        context["editar_url"] = reverse_lazy("editar_palabra")

        return context


class EditView(LoginRequiredMixin, TemplateView):
    template_name = "dictionary/edit.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        palabra_id = self.request.session.get("palabra_actual", 0)
        palabra_obj = get_object_or_404(Palabra, id=palabra_id)

        palabra_dict = palabra_obj.palabra_dict(usuario)
        context["palabra"] = palabra_dict

        element_list = []
        for element in palabra_obj.significados_objetos_usuario(usuario):
            element_list.append({"id": element.id, "text": element.significado})

        context["significados_usuario"] = element_list

        element_list = []
        for element in palabra_obj.lecturas_objetos_usuario(usuario):
            element_list.append({"id": element.id, "text": element.lectura})

        context["lecturas_usuario"] = element_list

        element_list = []
        for element in palabra_obj.notas_objetos_usuario(usuario):
            element_list.append({"id": element.id, "text": element.nota})

        context["notas_usuario"] = element_list

        etiquetas_list = palabra_obj.etiquetas_objetos(usuario)
        etiquetas_id_list = [e.etiqueta.id for e in etiquetas_list]
        new_etiquetas_list = Etiqueta.objects.filter(
            (Q(usuario=usuario) | Q(usuario__perfil__rol="admin"))
            & ~Q(id__in=etiquetas_id_list)
        ).order_by("etiqueta")
        new_etiquetas_str_list = [e.etiqueta for e in new_etiquetas_list]
        new_etiquetas_id = [e.id for e in new_etiquetas_list]
        new_etiquetas_list = dict(zip(new_etiquetas_str_list, new_etiquetas_id))
        self.request.session["new_etiquetas"] = new_etiquetas_list
        context["nuevas_etiquetas"] = new_etiquetas_str_list
        current_etiquetas_list = []
        etiquetas_user_list = palabra_obj.etiquetas_objetos_usuario(usuario)
        for etiqueta in etiquetas_user_list:
            current_etiquetas_list.append(
                {"id": etiqueta.id, "etiqueta": etiqueta.etiqueta}
            )
        context["current_etiquetas"] = current_etiquetas_list

        context["agregar_significado"] = reverse_lazy("agregar_significado")
        context["agregar_lectura"] = reverse_lazy("agregar_lectura")
        context["agregar_nota"] = reverse_lazy("agregar_nota")
        context["agregar_etiqueta"] = reverse_lazy("agregar_etiqueta")

        context["update_palabra"] = reverse_lazy("update_palabra")
        context["update_significado"] = reverse_lazy("update_significado")
        context["update_lectura"] = reverse_lazy("update_lectura")
        context["update_nota"] = reverse_lazy("update_nota")

        context["delete_palabra"] = reverse_lazy("delete_palabra")
        context["delete_significado"] = reverse_lazy("delete_significado")
        context["delete_lectura"] = reverse_lazy("delete_lectura")
        context["delete_nota"] = reverse_lazy("delete_nota")

        context["etiqueta_checks_url"] = reverse_lazy("toggle_etiqueta_en_palabra")

        context["detalles_url"] = reverse_lazy("detalles_palabra")
        return context


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "dictionary/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user

        context["crear_palabra_url"] = reverse_lazy("crear_palabra")
        context["toggle_modal_url"] = reverse_lazy("toggle_create_modal")

        ajustes_palabras = self.request.session.get("ajustes_palabras", {})

        context["intentado"] = ajustes_palabras.get("intentado", False)

        palabras = Palabra.objects.filter(
            (Q(usuario=usuario) | Q(usuario__perfil__rol="admin"))
        )
        index = ajustes_palabras.get("page_index", 0)
        index = ut.bound_page_index(index, len(palabras))
        ajustes_palabras["page_index"] = index
        context["index"] = index + 1

        palabras_list = []
        for palabra in palabras[index * 10 : min(len(palabras), index * 10 + 10)]:
            palabras_list.append(palabra.palabra_dict(usuario=usuario))
        context["palabras_list"] = palabras_list
        context["palabra_url"] = reverse_lazy("elegir_palabra")

        pages_list = ut.create_pages_list(index, len(palabras))
        context["show_pages_list"] = len(pages_list) > 1
        context["pages_list"] = pages_list

        context["cambiar_pagina_url"] = reverse_lazy("cambiar_pagina_palabras")

        context["ajustes_palabras"] = ajustes_palabras
        self.request.session["ajustes_palabras"] = ajustes_palabras
        print(dict(self.request.session))

        return context

    def is_mobile(request):
        user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
        return any(m in user_agent for m in ["mobile", "android", "iphone"])
