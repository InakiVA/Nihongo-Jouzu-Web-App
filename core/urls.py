from django.urls import path
from . import views

urlpatterns = [
    path("buscar/", views.busqueda_global, name="busqueda_global"),
]
