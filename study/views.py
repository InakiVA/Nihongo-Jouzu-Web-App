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


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "study/home.html"

    def asegurar_ajustes_sesion(self):
        ajustes_default = {
            "orden_elegido": "Creación",
            "descendente": False,
            "idioma_preguntas": "Original",
            "aleatorio": False,
            "filtros_palabras_andor": "AND",
            "filtros_palabras_inclusivo": True,
            "filtros_etiquetas_andor": "AND",
            "filtros_etiquetas_inclusivo": True,
        }
        if "inicio_ajustes" not in self.request.session:
            self.request.session["inicio_ajustes"] = ajustes_default.copy()
        else:
            for key, val in ajustes_default.items():
                self.request.session["inicio_ajustes"].setdefault(key, val)

    def crear_grupos_nuevos_del_admin(self):
        usuario = self.request.user
        ids_objetivo = set(
            Grupo.objects.filter(
                Q(usuario=usuario) | Q(usuario__perfil__rol="admin")
            ).values_list("id", flat=True)
        )  # que registro sea de admin o de usuario
        ids_existentes = set(
            UsuarioGrupo.objects.filter(usuario=usuario).values_list(
                "grupo_id", flat=True
            )
        )  # registros ya en tabla relacional
        ids_nuevos = ids_objetivo - ids_existentes

        if ids_nuevos:
            grupos_nuevos = Grupo.objects.filter(id__in=ids_nuevos).order_by("id")
            for grupo in grupos_nuevos:
                UsuarioGrupo.objects.create(
                    usuario=usuario,
                    grupo=grupo,
                    estudiando=False,
                    estrella=False,
                )

    def crear_palabras_nuevas_del_admin(self):
        usuario = self.request.user
        ids_objetivo = set(
            Palabra.objects.filter(
                Q(usuario=usuario) | Q(usuario__perfil__rol="admin")
            ).values_list("id", flat=True)
        )  # que registro sea de admin o de usuario
        ids_existentes = set(
            UsuarioPalabra.objects.filter(usuario=usuario).values_list(
                "palabra_id", flat=True
            )
        )  # registros ya en tabla relacional
        ids_nuevos = ids_objetivo - ids_existentes

        if ids_nuevos:
            palabras_nuevas = Palabra.objects.filter(id__in=ids_nuevos).order_by("id")
            for palabra in palabras_nuevas:
                UsuarioPalabra.objects.create(
                    usuario=usuario,
                    palabra=palabra,
                    progreso=0,
                    estrella=False,
                )

    def get_user_groups_list(self):
        usuario = self.request.user
        usuario_palabras = UsuarioPalabra.objects.filter(usuario=usuario)
        progreso_map = {up.palabra_id: up.progreso for up in usuario_palabras}

        usuario_grupos = (
            UsuarioGrupo.objects.filter(usuario=usuario)
            .select_related("grupo")  # para acceder a ug.grupo sin query extra
            .prefetch_related("grupo__grupo_palabras")  # para las palabras en el grupo
            .order_by("id")
        )

        grupos = []
        for ug in usuario_grupos:
            palabras = [gp.palabra_id for gp in ug.grupo.grupo_palabras.all()]
            progreso_total = sum(progreso_map.get(pid, 0) for pid in palabras)
            cantidad = len(palabras)
            progreso = int(progreso_total / cantidad) if cantidad > 0 else 0

            grupos.append(
                {
                    "text": ug.grupo.grupo,
                    "id": ug.grupo.id,
                    "progreso": progreso,
                    "estrella": ug.estrella,
                    "estudiando": ug.estudiando,
                    "fecha_creacion": ug.grupo.fecha_creacion,
                    "ultima_modificacion": ug.ultima_modificacion,
                    "autor": ug.grupo.usuario.username,
                }
            )
        return grupos

    def get_context_data(self, **kwargs):
        usuario = self.request.user
        self.asegurar_ajustes_sesion()
        ajustes = self.request.session["inicio_ajustes"]

        self.crear_palabras_nuevas_del_admin()
        self.crear_grupos_nuevos_del_admin()

        context = super().get_context_data(**kwargs)
        context["href_estudio"] = reverse_lazy("estudio")

        context["estudio_url"] = reverse_lazy("preparar_estudio")

        # __ Grupos_ajustes
        context["filtros_grupos"] = [
            {
                "text": filtro,
                "id": filtro + " (grupos)",
                "is_active": ajustes.get(filtro + " (grupos)", False),
                "url": reverse("toggle_filtro"),
            }
            for filtro in [
                "Elegidos",
                "Creados por mí",
                "Por completar",
                "Con estrella",
            ]
        ]
        context["select_orden_url"] = reverse("toggle_orden_grupos")
        orden_opciones = ("Creación", "Nombre", "Progreso", "Reciente")
        context["orden_opciones"] = orden_opciones
        orden_elegido = ajustes.get("orden_elegido", orden_opciones[0])
        context["orden_elegido"] = orden_elegido
        context["descendente_url"] = reverse("toggle_descendente")
        descendente = ajustes.get("descendente", False)
        context["on_descendente"] = descendente

        # __ Grupos_lista
        context["check_url"] = reverse("toggle_estudiando")
        context["estrella_url"] = reverse("toggle_estrella_grupo")

        grupos = self.get_user_groups_list()

        buscar_grupo_input = (
            self.request.GET.get("buscar_grupo", "").strip().lower()
        )  # search
        context["buscar_grupo_input"] = buscar_grupo_input
        if buscar_grupo_input:
            grupos = [g for g in grupos if buscar_grupo_input in g["text"].lower()]

        grupos_elegidos = [g for g in grupos if g["estudiando"]]
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
            grupos.sort(key=lambda g: g["id"], reverse=descendente)  # !! ojo

        context["grupos"] = grupos

        # __ Preguntas
        context["idioma_preguntas_url"] = reverse("toggle_idioma_preguntas")
        idioma_preguntas_opciones = ("Original", "Significados", "Cualquiera")
        context["idioma_preguntas_opciones"] = idioma_preguntas_opciones
        context["idioma_preguntas_elegido"] = self.request.session.get(
            "idioma_preguntas_elegido", idioma_preguntas_opciones[0]
        )
        context["aleatorio_url"] = reverse("toggle_aleatorio")
        context["is_aleatorio"] = ajustes.get("aleatorio", False)

        # __ Filtros
        context["filtros_palabras_andor_url"] = reverse("toggle_filtros_palabras_andor")
        context["filtros_palabras_inclusivo_url"] = reverse(
            "toggle_filtros_palabras_inclusivo"
        )
        context["on_filtros_palabras_andor"] = (
            ajustes.get("filtros_palabras_andor") == "OR"
        )
        context["on_filtros_palabras_inclusivo"] = (
            ajustes.get("filtros_palabras_inclusivo") == False
        )
        filtros_palabras = [
            {
                "text": filtro,
                "id": filtro + " (palabras)",
                "is_active": ajustes.get(filtro + " (palabras)", False),
                "url": reverse("toggle_filtro"),
            }
            for filtro in [
                "Creadas por mí",
                "Por completar",
                "Con estrella",
            ]
        ]
        context["filtros_palabras"] = filtros_palabras

        context["filtros_etiquetas_andor_url"] = reverse(
            "toggle_filtros_etiquetas_andor"
        )
        context["filtros_etiquetas_inclusivo_url"] = reverse(
            "toggle_filtros_etiquetas_inclusivo"
        )
        etiquetas_andor_switch_value = ajustes.get("filtros_etiquetas_andor") == "OR"
        etiquetas_inclusivo_switch_value = (
            ajustes.get("filtros_etiquetas_inclusivo") == False
        )
        context["on_filtros_etiquetas_andor"] = etiquetas_andor_switch_value
        context["on_filtros_etiquetas_inclusivo"] = etiquetas_inclusivo_switch_value

        tags = []
        tags_objects = Etiqueta.objects.filter(
            Q(usuario=usuario) | Q(usuario__perfil__rol="admin")
        ).order_by("etiqueta")
        open_collapse = [etiquetas_andor_switch_value, etiquetas_inclusivo_switch_value]

        for tag in tags_objects:
            active = ajustes.get(f"{tag.etiqueta} (etiqueta)", False)
            tags.append(
                {
                    "text": tag.etiqueta,
                    "id": f"{tag.etiqueta} (etiqueta)",
                    "is_active": active,
                    "url": reverse("toggle_filtro"),
                }
            )
            open_collapse.append(active)

        context["tags"] = tags
        context["is_open_collapse"] = any(open_collapse)

        context["cantidad_palabras"] = len(op.get_palabras_a_estudiar(usuario, ajustes))
        cantidad_grupos_elegidos = len(grupos_elegidos)
        if cantidad_grupos_elegidos == 1:
            context["cantidad_grupos"] = f"{cantidad_grupos_elegidos} elegido"
        else:
            context["cantidad_grupos"] = f"{cantidad_grupos_elegidos} elegidos"

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
            "grupos": palabra_obj.grupos_str(usuario),
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

        context["finalizar_url"] = reverse_lazy("resultados")

        context["index"] = index + 1
        context["index_porcentaje"] = ((index + 1) / len(palabras_ids)) * 100
        context["cambiar_pregunta_url"] = reverse_lazy("cambiar_pregunta")
        context["cambiar_progreso_url"] = reverse_lazy("cambiar_progreso")
        context["checar_pregunta_url"] = reverse("checar_pregunta")
        context["estrella_url"] = reverse("toggle_estrella_palabra")

        context["agregar_significado"] = reverse("agregar_significado")
        context["agregar_lectura"] = reverse("agregar_lectura")
        context["agregar_nota"] = reverse("agregar_nota")
        context["agregar_etiqueta"] = reverse("agregar_etiqueta")

        print(dict(self.request.session))
        return context

    def is_mobile(request):
        user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
        return user_agent in set("mobile", "android", "iphone")
