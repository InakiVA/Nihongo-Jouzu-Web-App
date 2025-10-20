from django.contrib import admin
from groups.models import Grupo, GrupoPalabra, UsuarioGrupo
from core.admin_mixins import UsuarioMixin, PalabraMixin, GrupoMixin, UsuarioMixin


@admin.register(Grupo)
class GrupoAdmin(UsuarioMixin):
    list_display = (
        "id",
        "grupo",
        "usuario_username",
        "fecha_creacion",
        "ultima_modificacion",
    )
    search_fields = ("grupo", "usuario__username")
    ordering = ("id",)


@admin.register(UsuarioGrupo)
class UsuarioGrupoAdmin(UsuarioMixin, GrupoMixin):
    list_display = (
        "id",
        "usuario_username",
        "grupo_grupo",
        "estudiando",
        "estrella",
        "fecha_creacion",
        "ultima_modificacion",
    )
    search_fields = ("grupo__grupo", "usuario__username")
    ordering = ("usuario__username", "grupo_id")


@admin.register(GrupoPalabra)
class GrupoPalabraAdmin(GrupoMixin, PalabraMixin):
    list_display = (
        "id",
        "grupo_grupo",
        "palabra_palabra",
        "fecha_creacion",
        "ultima_modificacion",
    )
    search_fields = ("grupo__grupo", "palabra__palabra")
    ordering = ("grupo_id", "palabra_id")
