from django.urls import path
from . import views

urlpatterns = [
    path("estudio", views.HomeView.as_view(), name="estudio"),
    path("diccionario", views.HomeView.as_view(), name="diccionario"),
    path("grupos", views.HomeView.as_view(), name="grupos"),
    path("usuario", views.HomeView.as_view(), name="usuario"),
]
