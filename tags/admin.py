from django.contrib import admin
from tags.models import Etiqueta, PalabraEtiqueta, GrupoEtiqueta
from core.admin_mixins import UsuarioMixin, PalabraMixin, EtiquetaMixin, GrupoMixin


@admin.register(Etiqueta)
class EtiquetaAdmin(UsuarioMixin):
    list_display = ("etiqueta", "usuario")
    search_fields = ("etiqueta", "usuario__username")
    ordering = ("etiqueta",)


@admin.register(PalabraEtiqueta)
class PalabraEtiquetaAdmin(PalabraMixin, EtiquetaMixin):
    list_display = ("palabra_palabra", "etiqueta_etiqueta", "usuario")
    search_fields = ("palabra__palabra", "etiqueta__etiqueta", "usuario__username")
    ordering = ("palabra_id", "etiqueta__etiqueta", "usuario__username")


@admin.register(GrupoEtiqueta)
class GrupoEtiquetaAdmin(GrupoMixin, EtiquetaMixin):
    list_display = ("grupo_grupo", "etiqueta_etiqueta", "usuario")
    search_fields = ("grupo__grupo", "etiqueta__etiqueta", "usuario__username")
    ordering = ("grupo_id", "etiqueta__etiqueta", "usuario__username")
