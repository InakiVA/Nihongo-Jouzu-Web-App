from django.urls import path
from . import views
import core.components as cp
import dictionary.operations as d_op

urlpatterns = [
    path("", views.HomeView.as_view(), name="palabras"),
    path("detalles", views.DetailView.as_view(), name="detalles"),
    path("crear-palabra", views.crear_palabra, name="crear_palabra"),
    path("toggle-modal", views.toggle_modal, name="toggle_modal"),
    path(
        "toggle-palabra-en-grupo",
        cp.toggle_checkbox,
        {"checkbox": "palabra_en_grupo"},
        name="toggle_palabra_en_grupo",
    ),
]
