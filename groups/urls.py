from django.urls import path
from . import views

urlpatterns = [
    path("", views.GroupsView.as_view(), name="grupos"),
]
