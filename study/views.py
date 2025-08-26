from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.db.models import Q

from django.shortcuts import get_object_or_404

from tags.models import Etiqueta
from groups.models import Grupo, UsuarioGrupo
from dictionary.models import Palabra
from progress.models import UsuarioPalabra

import study.operations as op
import core.operations as c_op


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "study/home.html"

    def get_context_data(self, **kwargs):
        usuario = self.request.user
        c_op.asegurar_ajustes_sesion(self.request)
        ajustes = self.request.session["inicio_ajustes"]

        c_op.crear_palabras_nuevas_del_admin(usuario)
        c_op.crear_grupos_nuevos_del_admin(usuario)

        context = super().get_context_data(**kwargs)
        context["href_estudio"] = reverse_lazy("estudio")

        context["estudio_url"] = reverse_lazy("preparar_estudio")

        # __ Grupos_ajustes
        context["filtros_grupos"] = [
            {
                "text": filtro,
                "id": filtro + " (grupos)",
                "is_active": ajustes.get(filtro + " (grupos)", False),
                "url": reverse_lazy("toggle_filtro"),
            }
            for filtro in [
                "Elegidos",
                "Creados por mí",
                "Por completar",
                "Con estrella",
            ]
        ]
        context["select_orden_url"] = reverse_lazy("toggle_orden_grupos")
        orden_opciones = ("Creación", "Nombre", "Progreso", "Reciente")
        context["orden_opciones"] = orden_opciones
        orden_elegido = ajustes.get("orden_elegido", orden_opciones[0])
        context["orden_elegido"] = orden_elegido
        context["descendente_url"] = reverse_lazy("toggle_descendente")
        descendente = ajustes.get("descendente", False)
        context["on_descendente"] = descendente

        # __ Grupos_lista
        context["check_url"] = reverse_lazy("toggle_estudiando")
        context["estrella_url"] = reverse_lazy("toggle_estrella_grupo")

        grupos = c_op.get_user_groups_list(usuario)

        buscar_grupo_input = (
            self.request.GET.get("buscar_grupo", "").strip().lower()
        )  # search
        context["buscar_grupo_input"] = buscar_grupo_input
        if buscar_grupo_input:
            grupos = [g for g in grupos if buscar_grupo_input in g["text"].lower()]

        grupos_elegidos = [g for g in grupos if g["checked"]]
        if ajustes.get("Creados por mí (grupos)"):
            grupos = [g for g in grupos if g["autor"] == usuario.username]
        if ajustes.get("Por completar (grupos)"):
            grupos = [g for g in grupos if g["progreso"] < 100]
        if ajustes.get("Con estrella (grupos)"):
            grupos = [g for g in grupos if g["estrella"]]
        if ajustes.get("Elegidos (grupos)"):
            grupos = grupos_elegidos

        if orden_elegido == "Progreso":
            grupos.sort(key=lambda g: g["progreso"], reverse=descendente)
        elif orden_elegido == "Reciente":
            grupos.sort(
                key=lambda g: g["ultima_modificacion"], reverse=not descendente
            )  # porque de más reciente a menos reciente le pongo el not
        elif orden_elegido == "Nombre":
            grupos.sort(key=lambda g: g["text"].lower(), reverse=descendente)
        elif orden_elegido == "Creación":
            grupos.sort(key=lambda g: g["id"], reverse=descendente)
        grupos_id = [g["id"] for g in grupos]
        ajustes["grupos_filtrados"] = grupos_id

        context["grupos"] = grupos
        context["seleccionar_grupos_url"] = reverse_lazy("seleccionar_grupos")
        context["limpiar_grupos_url"] = reverse_lazy("limpiar_grupos")

        # __ Preguntas
        context["idioma_preguntas_url"] = reverse_lazy("toggle_idioma_preguntas")
        idioma_preguntas_opciones = ("Original", "Significados", "Cualquiera")
        context["idioma_preguntas_opciones"] = idioma_preguntas_opciones
        context["idioma_preguntas_elegido"] = self.request.session.get(
            "idioma_preguntas_elegido", idioma_preguntas_opciones[0]
        )
        context["aleatorio_url"] = reverse_lazy("toggle_aleatorio")
        context["is_aleatorio"] = ajustes.get("aleatorio", False)

        # __ Filtros
        context["filtros_palabras_andor_url"] = reverse_lazy(
            "toggle_filtros_palabras_andor"
        )
        context["filtros_palabras_exclusivo_url"] = reverse_lazy(
            "toggle_filtros_palabras_exclusivo"
        )
        palabras_or = ajustes.get("filtros_palabras_andor") == "OR"
        context["on_filtros_palabras_andor"] = palabras_or
        on_filtros_palabras_exclusivo = ajustes.get("filtros_palabras_exclusivo")
        context["on_filtros_palabras_exclusivo"] = on_filtros_palabras_exclusivo
        filtros_palabras = [
            {
                "text": filtro,
                "id": filtro + " (palabras)",
                "is_active": ajustes.get(filtro + " (palabras)", False),
                "url": reverse_lazy("toggle_filtro"),
            }
            for filtro in [
                "Creadas por mí",
                "Por completar",
                "Con estrella",
            ]
        ]
        context["filtros_palabras"] = filtros_palabras
        texto_palabras = ""
        filtros_palabras_prendidos = []
        for filtro in filtros_palabras:
            if filtro["is_active"]:
                filtros_palabras_prendidos.append(filtro["text"].lower())
        if filtros_palabras_prendidos:
            if on_filtros_palabras_exclusivo:
                texto_palabras = " no "
                if palabras_or:
                    text_union = " o no ".join(filtros_palabras_prendidos)
                else:
                    text_union = " y no ".join(filtros_palabras_prendidos)
                texto_palabras += text_union
            else:
                texto_palabras = " "
                if palabras_or:
                    text_union = " o ".join(filtros_palabras_prendidos)
                else:
                    text_union = " y ".join(filtros_palabras_prendidos)
                texto_palabras += text_union

        context["filtros_palabras_show"] = len(filtros_palabras_prendidos) >= 2

        context["filtros_etiquetas_andor_url"] = reverse_lazy(
            "toggle_filtros_etiquetas_andor"
        )
        context["filtros_etiquetas_exclusivo_url"] = reverse_lazy(
            "toggle_filtros_etiquetas_exclusivo"
        )
        etiquetas_andor_switch_value = ajustes.get("filtros_etiquetas_andor") == "OR"
        etiquetas_exclusivo_switch_value = ajustes.get("filtros_etiquetas_exclusivo")
        context["on_filtros_etiquetas_andor"] = etiquetas_andor_switch_value
        context["on_filtros_etiquetas_exclusivo"] = etiquetas_exclusivo_switch_value

        tags = []
        tags_objects = Etiqueta.objects.filter(
            Q(usuario=usuario) | Q(usuario__perfil__rol="admin")
        ).order_by("etiqueta")
        etiquetas_elegidas = []

        for tag in tags_objects:
            active = ajustes.get(f"{tag.etiqueta} (etiqueta)", False)
            tags.append(
                {
                    "text": tag.etiqueta,
                    "id": f"{tag.etiqueta} (etiqueta)",
                    "is_active": active,
                    "url": reverse_lazy("toggle_filtro"),
                }
            )
            if active:
                etiquetas_elegidas.append(tag.etiqueta)

        if texto_palabras and etiquetas_elegidas:
            if etiquetas_exclusivo_switch_value:
                texto_palabras += " y sin"
            else:
                texto_palabras += " y con"
            if len(etiquetas_elegidas) >= 2:
                if etiquetas_andor_switch_value:
                    texto_palabras += " al menos una de las etiquetas elegidas"
                else:
                    texto_palabras += " todas las etiquetas elegidas"
            elif len(etiquetas_elegidas) == 1:
                texto_palabras += " la etiqueta elegida"
        elif etiquetas_elegidas:
            if etiquetas_exclusivo_switch_value:
                texto_palabras += " sin"
            else:
                texto_palabras += " con"
            if len(etiquetas_elegidas) >= 2:
                if etiquetas_andor_switch_value:
                    texto_palabras += " al menos una de las etiquetas elegidas"
                else:
                    texto_palabras += " todas las etiquetas elegidas"
            elif len(etiquetas_elegidas) == 1:
                texto_palabras += " la etiqueta elegida"

        context["tags"] = tags
        context["is_open_collapse"] = bool(etiquetas_elegidas)
        context["filtros_etiquetas_show"] = len(etiquetas_elegidas) >= 2
        if not texto_palabras:
            texto_palabras = " palabras sin filtrar"
        cantidad_palabras_elegidas = len(op.get_palabras_a_estudiar(usuario, ajustes))
        if cantidad_palabras_elegidas == 1:
            context["texto_palabras"] = " palabra " + texto_palabras
        else:
            context["texto_palabras"] = " palabras " + texto_palabras
        context["cantidad_palabras"] = cantidad_palabras_elegidas

        cantidad_grupos_elegidos = len(grupos_elegidos)
        if cantidad_grupos_elegidos == 1:
            context["cantidad_grupos"] = f"{cantidad_grupos_elegidos} elegido"
        else:
            context["cantidad_grupos"] = f"{cantidad_grupos_elegidos} elegidos"

        self.request.session["inicio_ajustes"] = ajustes

        print(dict(self.request.session))

        return context

    def is_mobile(request):
        user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
        return user_agent in set("mobile", "android", "iphone", "ipad")


class ResultadosView(LoginRequiredMixin, TemplateView):
    template_name = "study/resultados.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user

        # Palabras de sesión
        palabras_inputs_dict = self.request.session.get("respuestas_incorrectas", {})

        # -- esto solo es para ordenar por más intentos incorrectos primero
        palabras_inputs_list = list(
            zip(palabras_inputs_dict, palabras_inputs_dict.values())
        )
        palabras_inputs_list = sorted(
            palabras_inputs_list, key=lambda x: len(x[1]), reverse=True
        )
        palabras_inputs_dict = dict(palabras_inputs_list)
        # -- fin de orden

        # Palabras que están contestadas o previamente intentadas pero mal
        palabras_contestadas = self.request.session.get("palabras_contestadas", {})
        palabras_contestadas_list = []
        for palabra_id in palabras_contestadas:
            if (
                palabras_contestadas[palabra_id]
                or len(palabras_inputs_dict[palabra_id]) > 0
            ):
                palabras_contestadas_list.append(palabra_id)
        palabras_contestadas_total = max(len(palabras_contestadas_list), 1)

        palabras_incorrectas_id = []
        palabras_correctas_id = []
        for palabra in palabras_contestadas_list:
            if len(palabras_inputs_dict[palabra]) > 0:
                palabras_incorrectas_id.append(palabra)
            else:
                palabras_correctas_id.append(palabra)
        calificacion = int(
            (len(palabras_correctas_id) / palabras_contestadas_total) * 100
        )

        context["calificacion"] = calificacion
        context["balance"] = (
            f"{len(palabras_correctas_id)} de {len(palabras_contestadas_list)}"
        )

        palabras_incorrectas = []
        palabras_correctas = []

        for palabra_id in palabras_incorrectas_id:
            palabra_obj = get_object_or_404(Palabra, id=palabra_id)
            palabras_incorrectas.append(
                {
                    "id": palabra_obj.id,
                    "palabra": palabra_obj.palabra,
                    "significados": palabra_obj.significados_str(usuario),
                    "lecturas": palabra_obj.lecturas_str(usuario),
                    "etiquetas": palabra_obj.etiquetas_list(usuario),
                    "notas": palabra_obj.notas_str(usuario),
                    "progreso": palabra_obj.palabra_usuarios.get(
                        usuario=self.request.user
                    ).progreso,
                    "estrella": palabra_obj.palabra_usuarios.get(
                        usuario=self.request.user
                    ).estrella,
                    "incorrectas": ", ".join(palabras_inputs_dict[palabra_id]),
                }
            )

        for palabra_id in palabras_correctas_id:
            palabra_obj = get_object_or_404(Palabra, id=palabra_id)
            palabras_correctas.append(
                {
                    "id": palabra_obj.id,
                    "palabra": palabra_obj.palabra,
                    "significados": palabra_obj.significados_str(usuario),
                    "lecturas": palabra_obj.lecturas_str(usuario),
                    "etiquetas": palabra_obj.etiquetas_list(usuario),
                    "notas": palabra_obj.notas_str(usuario),
                    "progreso": palabra_obj.palabra_usuarios.get(
                        usuario=self.request.user
                    ).progreso,
                    "estrella": palabra_obj.palabra_usuarios.get(
                        usuario=self.request.user
                    ).estrella,
                }
            )

        context["incorrectas"] = palabras_incorrectas
        context["correctas"] = palabras_correctas
        context["palabra_url"] = reverse_lazy("elegir_palabra")

        print(dict(self.request.session))

        return context

    def is_mobile(request):
        user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
        return user_agent in set("mobile", "android", "iphone", "ipad")


class SesionView(LoginRequiredMixin, TemplateView):
    template_name = "study/sesion.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        index = self.request.session.get("index_palabra_pregunta", 0)
        palabras_ids = self.request.session.get("palabras_a_estudiar", [])
        palabra_id = self.request.session.get("palabra_actual")
        palabras_contestadas = self.request.session.get("palabras_contestadas", {})
        palabras_correctas = self.request.session.get("palabras_correctas", {})
        respuestas_incorrectas = self.request.session.get("respuestas_incorrectas", {})

        palabra_obj = get_object_or_404(Palabra, id=palabra_id)
        is_kanji = palabra_obj.palabra_etiquetas.filter(
            etiqueta__etiqueta="Kanji"
        ).exists()
        pregunta_lenguaje = self.request.session.get(
            "idioma_preguntas_elegido", "Original"
        )
        palabra_obj.set_pregunta_respuesta(pregunta_lenguaje, usuario, is_kanji)

        pregunta_list = palabra_obj.pregunta
        if len(pregunta_list) > 1:
            lectura_pregunta = f"{str(pregunta_list[1])}"
        else:
            lectura_pregunta = None

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

        palabra_dict = {
            "id": palabra_id,
            "is_kanji": is_kanji,
            "palabra": palabra_obj.palabra,
            "significados": palabra_obj.significados_str(usuario),
            "lecturas": palabra_obj.lecturas_str(usuario),
            "notas": palabra_obj.notas_str(usuario),
            "etiquetas": palabra_obj.etiquetas_list(usuario),
            "grupos": palabra_obj.grupos_list(usuario),
            "progreso": palabra_obj.palabra_usuarios.get(
                usuario=self.request.user
            ).progreso,
            "estrella": palabra_obj.palabra_usuarios.get(
                usuario=self.request.user
            ).estrella,
            "pregunta": str(pregunta_list[0]),
            "lecturas_pregunta": lectura_pregunta,
            "respuestas_incorrectas": ", ".join(
                respuestas_incorrectas[palabra_id],
            ),
        }

        context["palabra"] = palabra_dict
        context["palabra_contestada"] = palabras_contestadas[palabra_id]
        context["palabra_correcta"] = palabras_correctas[palabra_id]
        context["palabras_len"] = len(palabras_ids)
        self.request.session["respuestas"] = palabra_obj.respuestas

        palabras_relacionadas = palabra_obj.palabras_relacionadas(usuario)
        palabras_relacionadas_dict_list = []
        for palabra in palabras_relacionadas:
            palabras_relacionadas_dict_list.append(
                {
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
        new_grupos_list = {}
        new_grupos_str = []
        for grupo in grupos_usuario:
            if grupo in grupos_de_palabra_de_usuario:
                grupos_checks.append(
                    {
                        "id": grupo.id,
                        "text": grupo.grupo,
                        "is_selected": True,
                    }
                )
            else:
                new_grupos_list[grupo.grupo] = grupo.id
                new_grupos_str.append(grupo.grupo)

        context["nuevos_grupos"] = new_grupos_str
        self.request.session["new_grupos"] = new_grupos_list
        context["agregar_grupo"] = reverse_lazy("agregar_grupo")
        context["grupos_checks"] = grupos_checks
        context["grupos_checks_url"] = reverse_lazy("toggle_palabra_en_grupo")

        context["finalizar_url"] = reverse_lazy("resultados")

        context["index"] = index + 1
        context["index_porcentaje"] = ((index + 1) / len(palabras_ids)) * 100
        context["cambiar_pregunta_url"] = reverse_lazy("cambiar_pregunta")
        context["cambiar_progreso_url"] = reverse_lazy("cambiar_progreso")
        context["checar_pregunta_url"] = reverse("checar_pregunta")
        context["estrella_url"] = reverse_lazy("toggle_estrella_palabra")

        context["agregar_significado"] = reverse_lazy("agregar_significado")
        context["agregar_lectura"] = reverse_lazy("agregar_lectura")
        context["agregar_nota"] = reverse_lazy("agregar_nota")
        context["agregar_etiqueta"] = reverse_lazy("agregar_etiqueta")

        return context

    def is_mobile(request):
        user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
        return user_agent in set("mobile", "android", "iphone")
