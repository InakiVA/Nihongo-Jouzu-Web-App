# accounts/models.py
from django.db import models
from django.contrib.auth.models import User as Usuario


class RolPerfil(models.TextChoices):
    ADMIN = "admin", "Admin"
    USER = "user", "User"
    MODERATOR = "moderator", "Moderator"


class Perfil(models.Model):
    usuario = models.OneToOneField(
        Usuario, on_delete=models.CASCADE, related_name="perfil"
    )
    rol = models.CharField(
        max_length=10,
        choices=RolPerfil.choices,
        default=RolPerfil.USER,
    )

    def __str__(self):
        return f"{self.usuario.username} - {self.rol}"
