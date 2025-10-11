from django.contrib import admin
from core.admin_mixins import UsuarioMixin, PalabraMixin
from dictionary.models import Palabra, Significado, Lectura, Nota


@admin.register(Palabra)
class PalabraAdmin(UsuarioMixin):
    list_display = (
        "id",
        "palabra",
        "usuario",
        "fecha_creacion",
        "ultima_modificacion",
    )
    search_fields = ("palabra", "usuario__username")
    ordering = ("id", "palabra")


@admin.register(Significado)
class SignificadoAdmin(UsuarioMixin, PalabraMixin):
    list_display = (
        "id",
        "palabra",
        "significado",
        "usuario",
        "fecha_creacion",
        "ultima_modificacion",
    )
    search_fields = ("significado", "palabra__palabra", "usuario__username")
    ordering = ("id", "palabra_id", "usuario__username", "significado")


@admin.register(Lectura)
class LecturaAdmin(UsuarioMixin, PalabraMixin):
    list_display = (
        "id",
        "palabra",
        "lectura",
        "lectura_limpia",
        "usuario",
        "fecha_creacion",
        "ultima_modificacion",
    )
    search_fields = (
        "lectura",
        "lectura_limpia",
        "palabra__palabra",
        "usuario__username",
    )
    ordering = ("id", "palabra_id", "usuario__username", "lectura")


@admin.register(Nota)
class NotaAdmin(UsuarioMixin, PalabraMixin):
    list_display = (
        "id",
        "palabra",
        "nota",
        "usuario",
        "fecha_creacion",
        "ultima_modificacion",
    )
    search_fields = ("nota", "palabra__palabra", "usuario__username")
    ordering = ("id", "palabra_id", "usuario__username", "nota")
