from django.urls import path
from groups import views

urlpatterns = [
    path("", views.GroupsView.as_view(), name="grupos"),
    path("detalles-grupo", views.DetailView.as_view(), name="detalles_grupo"),
]
