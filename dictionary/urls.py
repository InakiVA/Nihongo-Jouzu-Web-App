from django.urls import path
from . import views
import dictionary.operations as d_op
import core.components as c_cp

urlpatterns = [
    path("", views.HomeView.as_view(), name="palabras"),
    path("crear-palabra", d_op.crear_palabra, name="crear_palabra"),
    path("detalles-palabra/", views.DetailView.as_view(), name="detalles_palabra"),
    path("editar-palabra/", views.EditView.as_view(), name="editar_palabra"),
    # __ updates
    path(
        "update-palabra",
        d_op.editar_palabra_atributos,
        {"atributo": "palabra"},
        name="update_palabra",
    ),
    path(
        "update-significado",
        d_op.editar_palabra_atributos,
        {"atributo": "significado"},
        name="update_significado",
    ),
    path(
        "update-lectura",
        d_op.editar_palabra_atributos,
        {"atributo": "lectura"},
        name="update_lectura",
    ),
    path(
        "update-nota",
        d_op.editar_palabra_atributos,
        {"atributo": "nota"},
        name="update_nota",
    ),
    # __ deletes
    path(
        "delete-palabra",
        d_op.eliminar_palabra_atributos,
        {"atributo": "palabra"},
        name="delete_palabra",
    ),
    path(
        "delete-significado",
        d_op.eliminar_palabra_atributos,
        {"atributo": "significado"},
        name="delete_significado",
    ),
    path(
        "delete-lectura",
        d_op.eliminar_palabra_atributos,
        {"atributo": "lectura"},
        name="delete_lectura",
    ),
    path(
        "delete-nota",
        d_op.eliminar_palabra_atributos,
        {"atributo": "nota"},
        name="delete_nota",
    ),
]
