from django.urls import path
from groups import views

import groups.operations as g_op
import core.components as c_cp

urlpatterns = [
    path("", views.GroupsView.as_view(), name="grupos"),
    path("detalles-grupo/", views.DetailView.as_view(), name="detalles_grupo"),
    path("editar-grupo/", views.EditView.as_view(), name="editar_grupo"),
    path("crear-grupo", g_op.crear_grupo, name="crear_grupo"),
    path(
        "update-grupo",
        g_op.editar_grupo_atributos,
        {"atributo": "grupo"},
        name="update_grupo",
    ),
    path(
        "update-descripcion",
        g_op.editar_grupo_atributos,
        {"atributo": "descripcion"},
        name="update_descripcion",
    ),
    path(
        "delete-grupo",
        g_op.eliminar_grupo,
        name="delete_grupo",
    ),
    path(
        "toggle-grupo-tiene-palabra",
        c_cp.toggle_checkbox,
        {"checkbox": "grupo_tiene_palabra"},
        name="toggle_grupo_tiene_palabra",
    ),
]
