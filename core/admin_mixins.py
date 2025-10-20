# core/admin_mixins.py
from django.contrib import admin


class UsuarioMixin(admin.ModelAdmin):
    list_select_related = ("usuario",)

    def usuario_username(self, obj):
        return obj.usuario.username

    usuario_username.short_description = "Usuario"
    usuario_username.admin_order_field = "usuario__username"


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

    palabra_palabra.short_description = "Palabra"
    palabra_palabra.admin_order_field = "palabra__palabra"


class GrupoMixin(admin.ModelAdmin):
    list_select_related = ("grupo",)

    def grupo_grupo(self, obj):
        return obj.grupo.grupo

    grupo_grupo.short_description = "Grupo"
    grupo_grupo.admin_order_field = "grupo__grupo"


class EtiquetaMixin(admin.ModelAdmin):
    list_select_related = ("etiqueta",)

    def etiqueta_etiqueta(self, obj):
        return obj.etiqueta.etiqueta

    etiqueta_etiqueta.short_description = "Etiqueta"
    etiqueta_etiqueta.admin_order_field = "etiqueta__etiqueta"
