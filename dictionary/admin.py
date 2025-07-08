from django.contrib import admin
from core.admin_mixins import AutorMixin, PalabraMixin
from dictionary.models import Palabra, Significado, Lectura, Nota


@admin.register(Palabra)
class PalabraAdmin(AutorMixin):
    list_display = ("palabra", "autor_username")
    search_fields = ("palabra", "autor__username")
    ordering = ("id",)


@admin.register(Significado)
class SignificadoAdmin(AutorMixin, PalabraMixin):
    list_display = ("palabra_palabra", "significado", "autor_username")
    search_fields = ("significado", "palabra__palabra", "autor__username")
    ordering = ("palabra_id", "autor__username", "significado")


@admin.register(Lectura)
class LecturaAdmin(AutorMixin, PalabraMixin):
    list_display = ("palabra_palabra", "lectura", "autor_username")
    search_fields = ("lectura", "palabra__palabra", "autor__username")
    ordering = ("palabra_id", "autor__username", "lectura")


@admin.register(Nota)
class NotaAdmin(AutorMixin, PalabraMixin):
    list_display = ("palabra_palabra", "nota", "autor_username")
    search_fields = ("nota", "palabra__palabra", "autor__username")
    ordering = ("palabra_id", "autor__username", "nota")
