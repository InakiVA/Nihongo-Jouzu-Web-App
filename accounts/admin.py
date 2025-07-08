from django.contrib import admin
from accounts.models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ("username", "role")
    search_fields = ("username", "role")
    ordering = ("username",)
