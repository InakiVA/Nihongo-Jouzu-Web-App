from django.urls import path
from groups import views

import groups.operations as g_op

urlpatterns = [
    path("", views.GroupsView.as_view(), name="grupos"),
    path("crear-grupo", g_op.crear_grupo, name="crear_grupo"),
    path("detalles-grupo/", views.DetailView.as_view(), name="detalles_grupo"),
]
