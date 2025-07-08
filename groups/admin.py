from django.contrib import admin
from groups.models import Grupo, GrupoPalabra, UsuarioGrupo
from core.admin_mixins import AutorMixin, PalabraMixin, GrupoMixin, UsuarioMixin


@admin.register(Grupo)
class GrupoAdmin(AutorMixin):
    list_display = ("grupo", "autor_username")
    search_fields = ("grupo", "autor__username")
    ordering = ("id",)


@admin.register(UsuarioGrupo)
class UsuarioGrupoAdmin(UsuarioMixin, GrupoMixin):
    list_display = ("grupo_grupo", "usuario_username", "guardado", "estudiando")
    search_fields = ("grupo__grupo", "usuario__username")
    ordering = ("usuario__username", "grupo_id")


@admin.register(GrupoPalabra)
class GrupoPalabraAdmin(GrupoMixin, PalabraMixin):
    list_display = ("grupo_grupo", "palabra_palabra")
    search_fields = ("grupo__grupo", "palabra__palabra")
    ordering = ("grupo_id", "palabra_id")
