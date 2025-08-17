from django.urls import path
from . import views
import core.components as cp
import study.operations as s_op

urlpatterns = [
    path("", views.HomeView.as_view(), name="inicio"),
    path("estudio/", views.SesionView.as_view(), name="estudio"),
    path("estudio/resultados/", views.ResultadosView.as_view(), name="resultados"),
    path("preparar-estudio/", s_op.preparar_estudio, name="preparar_estudio"),
    path("cambiar-pregunta/", s_op.cambiar_pregunta, name="cambiar_pregunta"),
    path("checar-pregunta/", s_op.checar_pregunta, name="checar_pregunta"),
]
