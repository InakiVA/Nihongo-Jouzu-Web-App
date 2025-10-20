from django.contrib import admin
from accounts.models import Perfil


@admin.register(Perfil)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ("id", "usuario", "rol")
    search_fields = ("usuario", "rol")
    ordering = ("usuario",)
