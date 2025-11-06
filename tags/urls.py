from django.urls import path
from tags import views

import tags.operations as e_op

urlpatterns = [
    path("", views.HomeView.as_view(), name="etiquetas"),
    path("crear-etiqueta", e_op.crear_etiqueta, name="crear_etiqueta"),
    path(
        "update-etiqueta",
        e_op.editar_etiqueta,
        {"atributo": "etiqueta"},
        name="update_etiqueta",
    ),
    path(
        "update-color",
        e_op.editar_etiqueta,
        {"atributo": "color"},
        name="update_color",
    ),
    path("eliminar-etiqueta", e_op.eliminar_etiqueta, name="eliminar_etiqueta"),
]
