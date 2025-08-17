from django.urls import path
from . import views
import core.components as cp
import dictionary.operations as d_op

urlpatterns = [
    path("", views.HomeView.as_view(), name="palabras"),
    path("detalles", views.DetailView.as_view(), name="detalles"),
    path("crear-palabra", d_op.crear_palabra, name="crear_palabra"),
]
