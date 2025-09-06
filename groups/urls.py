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
        "toggle-grupo-tiene-palabra",
        c_cp.toggle_checkbox,
        {"checkbox": "grupo_tiene_palabra"},
        name="toggle_grupo_tiene_palabra",
    ),
]
