from django.urls import path
from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="inicio"),
    path("estudio/", views.SesionView.as_view(), name="estudio"),
    path("estudio/resultados/", views.ResultadosView.as_view(), name="resultados"),
    path("preparar-estudio/", views.preparar_estudio, name="preparar_estudio"),
    path("cambiar-pregunta/", views.cambiar_pregunta, name="cambiar_pregunta"),
    path("cambiar-progreso/", views.cambiar_progreso, name="cambiar_progreso"),
    path("checar-pregunta/", views.checar_pregunta, name="checar_pregunta"),
    path(
        "agregar-significado/",
        views.agregar_a_palabra,
        {"tipo": "Significado"},
        name="agregar_significado",
    ),
    path(
        "agregar-lectura/",
        views.agregar_a_palabra,
        {"tipo": "Lectura"},
        name="agregar_lectura",
    ),
    path(
        "agregar-nota/", views.agregar_a_palabra, {"tipo": "Nota"}, name="agregar_nota"
    ),
    path(
        "agregar-etiqueta/",
        views.agregar_a_palabra,
        {"tipo": "Etiqueta"},
        name="agregar_etiqueta",
    ),
    # __ Checkboxes
    path("toggle-estudiando/", views.toggle_estudiando, name="toggle_estudiando"),
    path("toggle-aleatorio/", views.toggle_aleatorio, name="toggle_aleatorio"),
    path(
        "toggle-palabra-en-grupo",
        views.toggle_palabra_en_grupo,
        name="toggle_palabra_en_grupo",
    ),
    # __ Switches
    path(
        "toggle-descendente/",
        views.toggle_inicio_switch,
        {"switch": "descendente"},
        name="toggle_descendente",
    ),
    path(
        "toggle-filtros-palabras-andor/",
        views.toggle_inicio_switch,
        {"switch": "filtros_palabras_andor"},
        name="toggle_filtros_palabras_andor",
    ),
    path(
        "toggle-filtros-palabras-inclusivo/",
        views.toggle_inicio_switch,
        {"switch": "filtros_palabras_inclusivo"},
        name="toggle_filtros_palabras_inclusivo",
    ),
    path(
        "toggle-filtros-etiquetas-andor/",
        views.toggle_inicio_switch,
        {"switch": "filtros_etiquetas_andor"},
        name="toggle_filtros_etiquetas_andor",
    ),
    path(
        "toggle-filtros-etiquetas-inclusivo/",
        views.toggle_inicio_switch,
        {"switch": "filtros_etiquetas_inclusivo"},
        name="toggle_filtros_etiquetas_inclusivo",
    ),
    # __ Swaps
    path(
        "toggle-estrella-grupo/",
        views.toggle_estrella_grupo,
        name="toggle_estrella_grupo",
    ),
    path(
        "toggle-estrella-palabra/",
        views.toggle_estrella_palabra,
        name="toggle_estrella_palabra",
    ),
    path("toggle-filtro/", views.toggle_filtro, name="toggle_filtro"),
    # __ Selects
    path("toggle-orden/", views.toggle_orden_select, name="toggle_orden_select"),
    path(
        "toggle-idioma-preguntas/",
        views.toggle_idioma_preguntas,
        name="toggle_idioma_preguntas",
    ),
]
