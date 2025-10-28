from django.urls import path
from tags import views

import tags.operations as e_op

urlpatterns = [
    path("", views.HomeView.as_view(), name="etiquetas"),
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
]
