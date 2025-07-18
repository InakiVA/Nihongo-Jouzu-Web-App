from django.urls import path
from . import views
from dictionary import views as dict_views

urlpatterns = [
    path("", views.HomeView.as_view(), name="estudio"),
]
