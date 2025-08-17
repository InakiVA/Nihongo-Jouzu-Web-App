from django.urls import path
import core.operations as c_op
import core.components as c_cp

urlpatterns = [
    # __ atributos de palabra
    path(
        "agregar-significado/",
        c_op.agregar_a_palabra,
        {"tipo": "Significado"},
        name="agregar_significado",
    ),
    path(
        "agregar-lectura/",
        c_op.agregar_a_palabra,
        {"tipo": "Lectura"},
        name="agregar_lectura",
    ),
    path(
        "agregar-nota/", c_op.agregar_a_palabra, {"tipo": "Nota"}, name="agregar_nota"
    ),
    path(
        "agregar-etiqueta/",
        c_op.agregar_a_palabra,
        {"tipo": "Etiqueta"},
        name="agregar_etiqueta",
    ),
    path("cambiar-progreso/", c_op.cambiar_progreso, name="cambiar_progreso"),
    # __ funcionalidades
    path("toggle-modal", c_op.toggle_modal, name="toggle_modal"),
    path("elegir-palabra", c_op.elegir_palabra, name="elegir_palabra"),
    path("switch-palabras-page", c_op.cambiar_pagina, name="cambiar_pagina"),
    # __ Checkboxes
    path(
        "toggle-estudiando/",
        c_cp.toggle_checkbox,
        {"checkbox": "estudiando"},
        name="toggle_estudiando",
    ),
    path(
        "toggle-aleatorio/",
        c_cp.toggle_checkbox,
        {"checkbox": "aleatorio"},
        name="toggle_aleatorio",
    ),
    path(
        "toggle-palabra-en-grupo",
        c_cp.toggle_checkbox,
        {"checkbox": "palabra_en_grupo"},
        name="toggle_palabra_en_grupo",
    ),
    # __ Switches
    path(
        "toggle-descendente/",
        c_cp.toggle_switch,
        {"switch": "descendente"},
        name="toggle_descendente",
    ),
    path(
        "toggle-filtros-palabras-andor/",
        c_cp.toggle_switch,
        {"switch": "filtros_palabras_andor"},
        name="toggle_filtros_palabras_andor",
    ),
    path(
        "toggle-filtros-palabras-inclusivo/",
        c_cp.toggle_switch,
        {"switch": "filtros_palabras_inclusivo"},
        name="toggle_filtros_palabras_inclusivo",
    ),
    path(
        "toggle-filtros-etiquetas-andor/",
        c_cp.toggle_switch,
        {"switch": "filtros_etiquetas_andor"},
        name="toggle_filtros_etiquetas_andor",
    ),
    path(
        "toggle-filtros-etiquetas-inclusivo/",
        c_cp.toggle_switch,
        {"switch": "filtros_etiquetas_inclusivo"},
        name="toggle_filtros_etiquetas_inclusivo",
    ),
    # __ Swaps
    path(
        "toggle-estrella-grupo/",
        c_cp.toggle_estrella,
        {"objeto": "grupo"},
        name="toggle_estrella_grupo",
    ),
    path(
        "toggle-estrella-palabra/",
        c_cp.toggle_estrella,
        {"objeto": "palabra"},
        name="toggle_estrella_palabra",
    ),
    path(
        "toggle-filtro/", c_cp.toggle_filtro, {"view": "inicio"}, name="toggle_filtro"
    ),
    # __ Selects
    path(
        "toggle-orden-grupos/",
        c_cp.toggle_select,
        {"select": "orden_elegido"},
        name="toggle_orden_grupos",
    ),
    path(
        "toggle-idioma-preguntas/",
        c_cp.toggle_select,
        {"select": "idioma_preguntas_elegido"},
        name="toggle_idioma_preguntas",
    ),
]
