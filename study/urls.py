from django.urls import path
from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="estudio"),
    path("toggle-estudiando/", views.toggle_estudiando, name="toggle_estudiando"),
    path("toggle-estrella/", views.toggle_estrella, name="toggle_estrella"),
    path("toggle-aleatorio/", views.toggle_aleatorio, name="toggle_aleatorio"),
]
