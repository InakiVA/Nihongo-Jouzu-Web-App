from django.contrib import admin
from core.admin_mixins import UsuarioMixin, PalabraMixin
from dictionary.models import Palabra, Significado, Lectura, Nota


@admin.register(Palabra)
class PalabraAdmin(UsuarioMixin):
    list_display = (
        "palabra",
        "usuario",
        "fecha_creacion",
        "ultima_modificacion",
    )
    search_fields = ("palabra", "usuario__username")
    ordering = ("id",)


@admin.register(Significado)
class SignificadoAdmin(UsuarioMixin, PalabraMixin):
    list_display = (
        "palabra_id",
        "palabra",
        "id",
        "significado",
        "usuario",
        "fecha_creacion",
        "ultima_modificacion",
    )
    search_fields = ("significado", "palabra__palabra", "usuario__username")
    ordering = ("palabra_id", "usuario__username", "significado")


@admin.register(Lectura)
class LecturaAdmin(UsuarioMixin, PalabraMixin):
    list_display = (
        "palabra",
        "lectura",
        "usuario",
        "fecha_creacion",
        "ultima_modificacion",
    )
    search_fields = ("lectura", "palabra__palabra", "usuario__username")
    ordering = ("palabra_id", "usuario__username", "lectura")


@admin.register(Nota)
class NotaAdmin(UsuarioMixin, PalabraMixin):
    list_display = (
        "palabra",
        "nota",
        "usuario",
        "fecha_creacion",
        "ultima_modificacion",
    )
    search_fields = ("nota", "palabra__palabra", "usuario__username")
    ordering = ("palabra_id", "usuario__username", "nota")
