from django.contrib import admin
from tags.models import Etiqueta, PalabraEtiqueta
from core.admin_mixins import UsuarioMixin, PalabraMixin, EtiquetaMixin


@admin.register(Etiqueta)
class EtiquetaAdmin(UsuarioMixin):
    list_display = (
        "id",
        "etiqueta",
        "color",
        "usuario",
        "fecha_creacion",
        "ultima_modificacion",
    )
    search_fields = ("etiqueta", "usuario__username")
    ordering = ("etiqueta",)


@admin.register(PalabraEtiqueta)
class PalabraEtiquetaAdmin(PalabraMixin, EtiquetaMixin):
    list_display = (
        "id",
        "palabra_palabra",
        "etiqueta_etiqueta",
        "usuario",
        "fecha_creacion",
        "ultima_modificacion",
    )
    search_fields = ("palabra__palabra", "etiqueta__etiqueta", "usuario__username")
    ordering = ("palabra_id", "etiqueta__etiqueta", "usuario__username")
