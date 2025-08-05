from django.urls import path
from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="inicio"),
    path("estudio/pregunta/", views.PreguntaView.as_view(), name="estudio"),
    path("preparar-estudio/", views.preparar_estudio, name="preparar_estudio"),
    path("cambiar-pregunta/", views.cambiar_pregunta, name="cambiar_pregunta"),
    path("cambiar-progreso/", views.cambiar_progreso, name="cambiar_progreso"),
    # __ Checkboxes
    path("toggle-estudiando/", views.toggle_estudiando, name="toggle_estudiando"),
    path("toggle-aleatorio/", views.toggle_aleatorio, name="toggle_aleatorio"),
    # __ Switches
    path("toggle-descendente/", views.toggle_descendente, name="toggle_descendente"),
    path(
        "toggle-filtros-palabras/",
        views.toggle_filtros_palabras,
        name="toggle_filtros_palabras",
    ),
    path(
        "toggle-filtros-etiquetas/",
        views.toggle_filtros_etiquetas_switch,
        name="toggle_filtros_etiquetas_switch",
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
