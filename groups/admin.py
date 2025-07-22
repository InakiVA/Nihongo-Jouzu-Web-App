from django.contrib import admin
from groups.models import Grupo, GrupoPalabra, UsuarioGrupo
from core.admin_mixins import UsuarioMixin, PalabraMixin, GrupoMixin, UsuarioMixin


@admin.register(Grupo)
class GrupoAdmin(UsuarioMixin):
    list_display = ("grupo", "usuario_username")
    search_fields = ("grupo", "usuario__username")
    ordering = ("id",)


@admin.register(UsuarioGrupo)
class UsuarioGrupoAdmin(UsuarioMixin, GrupoMixin):
    list_display = ("usuario_username", "grupo_grupo", "estudiando", "estrella")
    search_fields = ("grupo__grupo", "usuario__username")
    ordering = ("usuario__username", "grupo_id")


@admin.register(GrupoPalabra)
class GrupoPalabraAdmin(GrupoMixin, PalabraMixin):
    list_display = ("grupo_grupo", "palabra_palabra")
    search_fields = ("grupo__grupo", "palabra__palabra")
    ordering = ("grupo_id", "palabra_id")
