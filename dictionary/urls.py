from django.urls import path
from . import views
import dictionary.operations as d_op
import core.components as c_cp

urlpatterns = [
    path("", views.HomeView.as_view(), name="palabras"),
    path("detalles", views.DetailView.as_view(), name="detalles"),
    path("crear-palabra", d_op.crear_palabra, name="crear_palabra"),
    path("editar", views.EditView.as_view(), name="editar"),
    # __ updates
    path(
        "update-palabra",
        d_op.editar_palabra_atributos,
        {"atributo": "palabra"},
        name="update_palabra",
    ),
    # __ deletes
    path(
        "delete-palabra",
        d_op.eliminar_palabra_atributos,
        {"atributo": "palabra"},
        name="delete_palabra",
    ),
]
