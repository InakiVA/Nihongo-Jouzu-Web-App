# accounts/models.py
from django.db import models
from django.contrib.auth.models import User as Usuario


class RolPerfil(models.TextChoices):
    ADMIN = "admin", "Admin"
    USER = "user", "User"
    MODERATOR = "moderator", "Moderator"


class ThemeChoice(models.TextChoices):
    JOUZU = "Jouzu", "Jouzu"
    MARINATE = "Marinate", "Marinate"
    TECHNO_PUNK = "Techno Punk", "Techno Punk"
    SPACE_COWBOY = "Space Cowboy", "Space Cowboy"
    CYBER_CLOCK = "Cyber Clock", "Cyber Clock"


class Perfil(models.Model):
    usuario = models.OneToOneField(
        Usuario, on_delete=models.CASCADE, related_name="perfil"
    )
    rol = models.CharField(
        max_length=10,
        choices=RolPerfil.choices,
        default=RolPerfil.USER,
    )
    tema = models.CharField(
        max_length=20,
        choices=ThemeChoice.choices,
        default=ThemeChoice.JOUZU,
    )

    def __str__(self):
        return f"{self.usuario.username} - {self.rol}"
