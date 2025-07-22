from django.contrib import admin
from core.admin_mixins import UsuarioMixin, PalabraMixin
from dictionary.models import Palabra, Significado, Lectura, Nota


@admin.register(Palabra)
class PalabraAdmin(UsuarioMixin):
    list_display = ("palabra", "usuario_username")
    search_fields = ("palabra", "usuario__username")
    ordering = ("id",)


@admin.register(Significado)
class SignificadoAdmin(UsuarioMixin, PalabraMixin):
    list_display = ("palabra_palabra", "significado", "usuario_username")
    search_fields = ("significado", "palabra__palabra", "usuario__username")
    ordering = ("palabra_id", "usuario__username", "significado")


@admin.register(Lectura)
class LecturaAdmin(UsuarioMixin, PalabraMixin):
    list_display = ("palabra_palabra", "lectura", "usuario_username")
    search_fields = ("lectura", "palabra__palabra", "usuario__username")
    ordering = ("palabra_id", "usuario__username", "lectura")


@admin.register(Nota)
class NotaAdmin(UsuarioMixin, PalabraMixin):
    list_display = ("palabra_palabra", "nota", "usuario_username")
    search_fields = ("nota", "palabra__palabra", "usuario__username")
    ordering = ("palabra_id", "usuario__username", "nota")
