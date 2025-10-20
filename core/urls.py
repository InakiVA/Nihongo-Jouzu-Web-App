from django.urls import path
import core.operations as c_op
import core.components as c_cp

urlpatterns = [
    # == atributos de palabra
    # __ create
    path(
        "agregar-significado",
        c_op.agregar_a_palabra,
        {"tipo": "significado"},
        name="agregar_significado",
    ),
    path(
        "agregar-lectura",
        c_op.agregar_a_palabra,
        {"tipo": "lectura"},
        name="agregar_lectura",
    ),
    path("agregar-nota", c_op.agregar_a_palabra, {"tipo": "nota"}, name="agregar_nota"),
    path(
        "agregar-etiqueta",
        c_op.agregar_a_palabra,
        {"tipo": "etiqueta"},
        name="agregar_etiqueta",
    ),
    path(
        "agregar-grupo",
        c_op.agregar_a_palabra,
        {"tipo": "grupo"},
        name="agregar_grupo",
    ),
    # __ update (están en diccionario)
    path("cambiar-progreso", c_op.cambiar_progreso, name="cambiar_progreso"),
    # == funcionalidades
    # __ elegir elemento
    path(
        "elegir-palabra",
        c_op.elemento_detalles,
        {"elemento": "palabra"},
        name="elegir_palabra",
    ),
    path(
        "elegir-grupo",
        c_op.elemento_detalles,
        {"elemento": "grupo"},
        name="elegir_grupo",
    ),
    path(
        "switch-palabras-page",
        c_op.cambiar_pagina,
        {"pagina": "palabras"},
        name="cambiar_pagina_palabras",
    ),
    path(
        "switch-grupos-page",
        c_op.cambiar_pagina,
        {"pagina": "grupos"},
        name="cambiar_pagina_grupos",
    ),
    path(
        "switch-buscar-page",
        c_op.cambiar_pagina,
        {"pagina": "buscar"},
        name="cambiar_pagina_buscar",
    ),
    # == Checkboxes
    path(
        "toggle-estudiando",
        c_cp.toggle_checkbox,
        {"checkbox": "estudiando"},
        name="toggle_estudiando",
    ),
    path(
        "toggle-aleatorio",
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
    path(
        "toggle-etiqueta-en-palabra",
        c_cp.toggle_checkbox,
        {"checkbox": "etiqueta_en_palabra"},
        name="toggle_etiqueta_en_palabra",
    ),
    # == Switches
    path(
        "toggle-descendente",
        c_cp.toggle_switch,
        {"switch": "descendente"},
        name="toggle_descendente",
    ),
    path(
        "toggle-filtros-palabras-andor",
        c_cp.toggle_switch,
        {"switch": "filtros_palabras_andor"},
        name="toggle_filtros_palabras_andor",
    ),
    path(
        "toggle-filtros-palabras-exclusivo",
        c_cp.toggle_switch,
        {"switch": "filtros_palabras_exclusivo"},
        name="toggle_filtros_palabras_exclusivo",
    ),
    path(
        "toggle-filtros-etiquetas-andor",
        c_cp.toggle_switch,
        {"switch": "filtros_etiquetas_andor"},
        name="toggle_filtros_etiquetas_andor",
    ),
    path(
        "toggle-filtros-etiquetas-exclusivo",
        c_cp.toggle_switch,
        {"switch": "filtros_etiquetas_exclusivo"},
        name="toggle_filtros_etiquetas_exclusivo",
    ),
    # == Swaps
    path(
        "toggle-estrella-grupo",
        c_cp.toggle_estrella,
        {"objeto": "grupo"},
        name="toggle_estrella_grupo",
    ),
    path(
        "toggle-estrella-palabra",
        c_cp.toggle_estrella,
        {"objeto": "palabra"},
        name="toggle_estrella_palabra",
    ),
    path("toggle-filtro", c_cp.toggle_filtro, {"view": "inicio"}, name="toggle_filtro"),
    # == Selects
    path(
        "toggle-orden-grupos",
        c_cp.toggle_select,
        {"select": "orden_elegido"},
        name="toggle_orden_grupos",
    ),
    path(
        "toggle-idioma-preguntas",
        c_cp.toggle_select,
        {"select": "idioma_preguntas_elegido"},
        name="toggle_idioma_preguntas",
    ),
]
