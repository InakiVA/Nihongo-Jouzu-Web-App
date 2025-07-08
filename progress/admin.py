from django.contrib import admin
from progress.models import UsuarioPalabra
from core.admin_mixins import UsuarioMixin, PalabraMixin


@admin.register(UsuarioPalabra)
class UsuarioPalabraAdmin(UsuarioMixin, PalabraMixin):
    list_display = ("palabra_palabra", "usuario_username", "progreso", "estrella")
    search_fields = ("palabra__palabra", "usuario__username")
    ordering = ("usuario__username", "palabra_id")
