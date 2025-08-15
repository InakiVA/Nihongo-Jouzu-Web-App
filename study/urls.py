from django.urls import path
from . import views
import core.components as cp
import study.operations as s_op

urlpatterns = [
    path("", views.HomeView.as_view(), name="inicio"),
    path("estudio/", views.SesionView.as_view(), name="estudio"),
    path("estudio/resultados/", views.ResultadosView.as_view(), name="resultados"),
    path("preparar-estudio/", s_op.preparar_estudio, name="preparar_estudio"),
    path("cambiar-pregunta/", s_op.cambiar_pregunta, name="cambiar_pregunta"),
    path("cambiar-progreso/", s_op.cambiar_progreso, name="cambiar_progreso"),
    path("checar-pregunta/", s_op.checar_pregunta, name="checar_pregunta"),
    path(
        "agregar-significado/",
        s_op.agregar_a_palabra,
        {"tipo": "Significado"},
        name="agregar_significado",
    ),
    path(
        "agregar-lectura/",
        s_op.agregar_a_palabra,
        {"tipo": "Lectura"},
        name="agregar_lectura",
    ),
    path(
        "agregar-nota/", s_op.agregar_a_palabra, {"tipo": "Nota"}, name="agregar_nota"
    ),
    path(
        "agregar-etiqueta/",
        s_op.agregar_a_palabra,
        {"tipo": "Etiqueta"},
        name="agregar_etiqueta",
    ),
    # __ Checkboxes
    path(
        "toggle-estudiando/",
        cp.toggle_checkbox,
        {"checkbox": "estudiando"},
        name="toggle_estudiando",
    ),
    path(
        "toggle-aleatorio/",
        cp.toggle_checkbox,
        {"checkbox": "aleatorio"},
        name="toggle_aleatorio",
    ),
    path(
        "toggle-palabra-en-grupo",
        cp.toggle_checkbox,
        {"checkbox": "palabra_en_grupo"},
        name="toggle_palabra_en_grupo",
    ),
    # __ Switches
    path(
        "toggle-descendente/",
        cp.toggle_switch,
        {"switch": "descendente"},
        name="toggle_descendente",
    ),
    path(
        "toggle-filtros-palabras-andor/",
        cp.toggle_switch,
        {"switch": "filtros_palabras_andor"},
        name="toggle_filtros_palabras_andor",
    ),
    path(
        "toggle-filtros-palabras-inclusivo/",
        cp.toggle_switch,
        {"switch": "filtros_palabras_inclusivo"},
        name="toggle_filtros_palabras_inclusivo",
    ),
    path(
        "toggle-filtros-etiquetas-andor/",
        cp.toggle_switch,
        {"switch": "filtros_etiquetas_andor"},
        name="toggle_filtros_etiquetas_andor",
    ),
    path(
        "toggle-filtros-etiquetas-inclusivo/",
        cp.toggle_switch,
        {"switch": "filtros_etiquetas_inclusivo"},
        name="toggle_filtros_etiquetas_inclusivo",
    ),
    # __ Swaps
    path(
        "toggle-estrella-grupo/",
        cp.toggle_estrella,
        {"objeto": "grupo"},
        name="toggle_estrella_grupo",
    ),
    path(
        "toggle-estrella-palabra/",
        cp.toggle_estrella,
        {"objeto": "palabra"},
        name="toggle_estrella_palabra",
    ),
    path("toggle-filtro/", cp.toggle_filtro, {"view": "inicio"}, name="toggle_filtro"),
    # __ Selects
    path(
        "toggle-orden-grupos/",
        cp.toggle_select,
        {"select": "orden_elegido"},
        name="toggle_orden_grupos",
    ),
    path(
        "toggle-idioma-preguntas/",
        cp.toggle_select,
        {"select": "idioma_preguntas_elegido"},
        name="toggle_idioma_preguntas",
    ),
]
