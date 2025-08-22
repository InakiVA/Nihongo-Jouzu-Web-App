from django.urls import path
from . import views
import dictionary.operations as d_op

urlpatterns = [
    path("", views.HomeView.as_view(), name="palabras"),
    path("detalles", views.DetailView.as_view(), name="detalles"),
    path("editar", views.EditView.as_view(), name="editar"),
    path("crear-palabra", d_op.crear_palabra, name="crear_palabra"),
]
