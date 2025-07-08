from django.contrib import admin
from .models import (
    Usuario,
    Palabra,
    Grupo,
    Etiqueta,
    Significado,
    Lectura,
    Nota,
    UsuarioPalabra,
    UsuarioGrupo,
    GrupoPalabra,
    PalabraEtiqueta,
    GrupoEtiqueta,
)


# __ MIXINS
class AutorMixin(admin.ModelAdmin):
    list_select_related = ("autor",)

    def autor_username(self, obj):
        return obj.autor.username

    autor_username.short_description = "Autor"
    autor_username.admin_order_field = "autor__username"


class UsuarioMixin(admin.ModelAdmin):
    list_select_related = ("usuario",)

    def usuario_username(self, obj):
        return obj.usuario.username

    usuario_username.short_description = "User"
    usuario_username.admin_order_field = "usuario__username"


class PalabraMixin(admin.ModelAdmin):
    list_select_related = ("palabra",)

    def palabra_palabra(self, obj):
        return obj.palabra.palabra

    def palabra_id(self, obj):
        return obj.palabra.id

    palabra_palabra.short_description = "Palabra"
    palabra_palabra.admin_order_field = "palabra__palabra"


class GrupoMixin(admin.ModelAdmin):
    list_select_related = ("grupo",)

    def grupo_grupo(self, obj):
        return obj.grupo.grupo

    def grupo_id(self, obj):
        return obj.grupo.id

    grupo_grupo.short_description = "Grupo"
    grupo_grupo.admin_order_field = "grupo__grupo"


class EtiquetaMixin(admin.ModelAdmin):
    list_select_related = ("etiqueta",)

    def etiqueta_etiqueta(self, obj):
        return obj.etiqueta.etiqueta

    def etiqueta_id(self, obj):
        return obj.palabra.id

    etiqueta_etiqueta.short_description = "Etiqueta"
    etiqueta_etiqueta.admin_order_field = "etiqueta__etiqueta"


# __ ADMIN PRINCIPALES
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ("username", "role")
    search_fields = ("username", "role")
    ordering = ("username",)


@admin.register(Palabra)
class PalabraAdmin(AutorMixin):
    list_display = ("palabra", "autor_username")
    search_fields = ("palabra", "autor__username")
    ordering = ("id",)


@admin.register(Grupo)
class GrupoAdmin(AutorMixin):
    list_display = ("grupo", "autor_username")
    search_fields = ("grupo", "autor__username")
    ordering = ("id",)


@admin.register(Etiqueta)
class EtiquetaAdmin(AutorMixin):
    list_display = ("etiqueta", "autor_username")
    search_fields = ("etiqueta", "autor__username")
    ordering = ("etiqueta",)


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


@admin.register(UsuarioPalabra)
class UsuarioPalabraAdmin(UsuarioMixin, PalabraMixin):
    list_display = ("palabra_palabra", "usuario_username", "progreso", "estrella")
    search_fields = ("palabra__palabra", "usuario__username")
    ordering = ("usuario__username", "palabra_id")


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


@admin.register(PalabraEtiqueta)
class PalabraEtiquetaAdmin(PalabraMixin, EtiquetaMixin):
    list_display = ("palabra_palabra", "etiqueta_etiqueta")
    search_fields = ("palabra__palabra", "etiqueta__etiqueta")
    ordering = ("palabra_id", "etiqueta__etiqueta")


@admin.register(GrupoEtiqueta)
class GrupoEtiquetaAdmin(GrupoMixin, EtiquetaMixin):
    list_display = ("grupo_grupo", "etiqueta_etiqueta")
    search_fields = ("grupo__grupo", "etiqueta__etiqueta")
    ordering = ("grupo_id", "etiqueta__etiqueta")
