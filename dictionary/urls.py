from django.urls import path
from . import views

urlpatterns = [
    path("diccionario", views.HomeView.as_view(), name="dictionary"),
]
