from django.urls import path
from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="palabras"),
    path("crear-palabra", views.crear_palabra, name="crear_palabra"),
    path("toggle-modal", views.toggle_modal, name="toggle_modal"),
]
